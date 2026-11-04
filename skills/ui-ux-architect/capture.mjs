// Capture screenshots, visible text and rendered-page measurements for a UI audit.
//
// Usage (from the audited repo's root, so `playwright-core` or `playwright` resolves):
//   node <skill-dir>/capture.mjs <outDir> <baseUrl> [routes] [widths] [themes]
//
//   baseUrl  e.g. https://preview-url.vercel.app — audit what shipped, not a dev server
//   routes   comma list, default "/"
//   widths   comma list, default "360,768,1440"
//   themes   comma list, default "" (the site's own default). Each value is written to
//            localStorage[THEME_KEY] before load (THEME_KEY defaults to "theme", next-themes)
//   CHROME   optional path to a Chromium binary, when the installed playwright wants a
//            browser revision that is not downloaded
//
// Writes <outDir>/<slug>-<width>-<theme>.png and .txt (visible text), and one measurements.json.
// Read-only: it never logs in, clicks, or submits.

import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
// Resolve Playwright from the audited repo (the current directory), not from this skill's
// folder: a bare import would look beside this file, where nothing is installed.
const requireFromCwd = createRequire(join(process.cwd(), "package.json"));
let chromium;
for (const pkg of ["playwright-core", "playwright"]) {
  try {
    const mod = await import(pathToFileURL(requireFromCwd.resolve(pkg)).href);
    chromium = mod.chromium ?? mod.default?.chromium; // CommonJS by path: named export sits on default
    if (chromium) break;
  } catch {}
}
if (!chromium) throw new Error("install playwright or playwright-core in the audited repo");

const [outDir, baseUrl, routesArg = "/", widthsArg = "360,768,1440", themesArg = ""] = process.argv.slice(2);
if (!outDir || !baseUrl) throw new Error("usage: capture.mjs <outDir> <baseUrl> [routes] [widths] [themes]");
const THEME_KEY = process.env.THEME_KEY || "theme";
// Bot-protection interstitials. Measuring one reports a clean page that was never seen.
const CHALLENGE = /Security Checkpoint|Just a moment|Attention Required|Verifying you are human/i;
mkdirSync(outDir, { recursive: true });

const HEIGHTS = { 360: 740, 375: 812, 390: 844, 414: 896, 768: 1024, 1024: 768, 1440: 900 };

// Runs inside the page. Everything here is measured from computed styles, not source.
function measure() {
  const vw = window.innerWidth;
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none" && s.opacity !== "0";
  };
  const describe = (el) => {
    const id = el.id ? `#${el.id}` : "";
    const cls = typeof el.className === "string" && el.className ? "." + el.className.trim().split(/\s+/).slice(0, 4).join(".") : "";
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  const textOf = (el) =>
    Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim())
      .join(" ")
      .trim();

  // Colour helpers for an approximate contrast check (ignores images and gradients).
  const parse = (c) => (c.match(/[\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => {
    const f = (v) => ((v /= 255) <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const bgOf = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.backgroundImage !== "none") return null; // cannot judge over an image
      const c = parse(s.backgroundColor);
      if (c.length >= 3 && (c[3] === undefined || c[3] >= 0.95)) return c;
    }
    return parse(getComputedStyle(document.body).backgroundColor);
  };

  // Text floor = 1.25rem (Tailwind text-xl), relative to the root: a site whose root is not
  // 16px renders every class at a different pixel size. Change the factor to the repo's floor.
  const rootPx = parseFloat(getComputedStyle(document.documentElement).fontSize);
  const floorPx = 1.25 * rootPx;
  const all = Array.from(document.querySelectorAll("body *"));
  const smallText = [];
  const lowContrast = [];
  const fontSizes = {};
  const families = {};
  const textColors = {};

  for (const el of all) {
    const t = textOf(el);
    if (!t || !visible(el) || el.closest(".sr-only")) continue;
    const s = getComputedStyle(el);
    const px = parseFloat(s.fontSize);
    fontSizes[px] = (fontSizes[px] || 0) + 1;
    const fam = s.fontFamily.split(",")[0].replace(/["']/g, "").trim();
    families[fam] = (families[fam] || 0) + 1;
    textColors[s.color] = (textColors[s.color] || 0) + 1;
    const exempt = el.closest(".safe-html-content pre, [aria-hidden='true']") ? "exempt-candidate" : null;
    if (px < floorPx - 0.1) smallText.push({ el: describe(el), px, rem: +(px / rootPx).toFixed(3), text: t.slice(0, 60), font: fam, note: exempt });
    const bg = bgOf(el);
    const fg = parse(s.color);
    if (bg && fg.length >= 3) {
      const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
      const ratio = (a + 0.05) / (b + 0.05);
      const large = px >= 24 || (px >= 18.66 && Number(s.fontWeight) >= 700);
      if (ratio < (large ? 3 : 4.5)) lowContrast.push({ el: describe(el), ratio: +ratio.toFixed(2), px, text: t.slice(0, 60) });
    }
  }

  const overflow = all
    .filter((el) => visible(el) && el.getBoundingClientRect().right > vw + 1)
    .map((el) => ({ el: describe(el), right: Math.round(el.getBoundingClientRect().right) }))
    .slice(0, 10);

  const targets = Array.from(document.querySelectorAll("a[href], button, input, select, textarea, [role=button], [role=tab]"))
    .filter(visible)
    .map((el) => ({ el, r: el.getBoundingClientRect() }))
    .filter(({ r }) => r.width < 44 || r.height < 44)
    .map(({ el, r }) => ({ el: describe(el), w: Math.round(r.width), h: Math.round(r.height), name: (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 40) }));

  const unnamed = Array.from(document.querySelectorAll("button, a[href], [role=button]"))
    .filter((el) => visible(el) && !(el.getAttribute("aria-label") || el.textContent.trim() || el.querySelector("img[alt]:not([alt=''])")))
    .map(describe);

  const imgNoAlt = Array.from(document.images).filter((i) => visible(i) && !i.hasAttribute("alt")).map((i) => i.src.split("/").pop());

  const headings = Array.from(document.querySelectorAll("h1,h2,h3")).filter(visible).map((h) => `${h.tagName}: ${h.textContent.trim().slice(0, 60)}`);

  return {
    title: document.title,
    rootPx,
    floorPx,
    htmlClass: document.documentElement.className,
    pageWidth: document.documentElement.scrollWidth,
    viewportWidth: vw,
    horizontalScroll: document.documentElement.scrollWidth > vw,
    overflow,
    headings,
    fontSizes,
    families,
    textColorCount: Object.keys(textColors).length,
    smallText: smallText.slice(0, 40),
    smallTextTotal: smallText.length,
    lowContrast: lowContrast.slice(0, 25),
    lowContrastTotal: lowContrast.length,
    smallTargets: targets.slice(0, 25),
    smallTargetsTotal: targets.length,
    unnamedControls: unnamed,
    imagesWithoutAlt: imgNoAlt,
  };
}

const browser = await chromium.launch({ executablePath: process.env.CHROME || undefined });
const results = [];
for (const theme of themesArg ? themesArg.split(",") : [""]) {
  for (const width of widthsArg.split(",").map(Number)) {
    const context = await browser.newContext({ viewport: { width, height: HEIGHTS[width] || 900 }, deviceScaleFactor: 1 });
    if (theme) await context.addInitScript(([k, t]) => localStorage.setItem(k, t), [THEME_KEY, theme]);
    for (const route of routesArg.split(",")) {
      const page = await context.newPage();
      const consoleErrors = [];
      page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text().slice(0, 200)));
      page.on("pageerror", (e) => consoleErrors.push(String(e).slice(0, 200)));
      const slug = route.replace(/^\//, "").replace(/[/\[\]]/g, "_") || "root";
      const shot = join(outDir, `${slug}-${width}-${theme || "default"}.png`);
      try {
        let res = await page.goto(baseUrl + route, { waitUntil: "load", timeout: 60000 });
        await page.waitForTimeout(2500); // let client components, fonts and rain settle
        // Bot protection (Vercel, Cloudflare) can serve a challenge page after many fast loads.
        // Wait it out or fail loudly; never measure it.
        for (let i = 0; i < 3 && CHALLENGE.test(await page.title()); i++) {
          await page.waitForTimeout(10000);
          res = await page.reload({ waitUntil: "load", timeout: 60000 });
          await page.waitForTimeout(2500);
        }
        if (CHALLENGE.test(await page.title())) throw new Error("bot-protection challenge did not clear: INCONCLUSIVE");
        const m = await page.evaluate(measure);
        writeFileSync(shot.replace(/\.png$/, ".txt"), await page.evaluate(() => document.body.innerText));
        await page.screenshot({ path: shot, fullPage: true });
        results.push({ route, width, theme, status: res?.status(), screenshot: shot, consoleErrors, ...m });
        console.log(`${res?.status()} ${route} ${width} ${theme} small=${m.smallTextTotal} contrast=${m.lowContrastTotal} targets=${m.smallTargetsTotal} hscroll=${m.horizontalScroll}`);
      } catch (e) {
        results.push({ route, width, theme, error: String(e).slice(0, 300) });
        console.log(`ERR ${route} ${width} ${theme}: ${String(e).slice(0, 120)}`);
      }
      await page.close();
    }
    await context.close();
  }
}
await browser.close();
writeFileSync(join(outDir, "measurements.json"), JSON.stringify(results, null, 2));
