---
name: ui-ux-architect
description: Audit UI/UX design for visual hierarchy, spacing, typography, and accessibility — Jobs/Ive-style design critique, judged from the rendered page and the repo's own design rules. Use when reviewing a screen's visual design or running a UX audit.
user-invocable: true
argument-hint: "[route, screen, flow, or \"full audit\"]"
metadata:
  version: "2.0.0"
---

# UI/UX Architect

Design audit judged from the **rendered page**, against the repo's own rules first and
general design taste second.

**Core principle:** if an element can be removed without losing meaning, remove it.

Borrowed, with credit:
- **gstack `/design-review`:** rendered-page evidence, three widths, graded categories, an
  AI-slop check, one fix per commit.
- **Cursor's `control-ui` / `verify-this`:** reuse the repo's harness first, falsifiable
  verdicts.
- **dyl-stack's visual judge:** check theme polarity first.

## Rules of evidence

1. **Conclude from the rendered page, not the source.** A class name says what someone
   intended; computed style says what shipped. Read source only to locate a fix.
2. **Audit what shipped.** For web, use the production URL or a PR preview, not a dev
   server: dev servers serve stale bundles and differ from production builds. Confirm the
   host is the app you mean, not a marketing site on a sibling domain.
3. **Use a browser, not curl.** Bot protection often answers curl with a challenge. A real
   browser usually passes, but after many fast loads it can be served a challenge page
   instead ("Security Checkpoint", "Just a moment"). A check run on that page finds nothing
   and looks clean. `capture.mjs` waits it out and fails loudly; any ad-hoc probe must check
   `document.title` before its result counts.
4. **Every finding has a verdict:** CONFIRMED (screenshot or measurement attached),
   PLAUSIBLE (seen but not measured), or INCONCLUSIVE (could not capture). Never drop an
   inconclusive item. Say "N of M routes checked", not "no issues".

## Phase 1: Discovery

Read the repo's own design rules before forming opinions: `CLAUDE.md` / `AGENTS.md`,
design or typography ADRs, `docs/*design*`, the theme setup (theme names, tokens,
`localStorage` key), and any project skills about layout, copy or UI. Write the rules down
as a table — they are decisions, and a generic design opinion does not override them.

Then list the routes or screens: the router or sitemap for web, the navigation graph for
native.

**Ask only when the repo cannot tell you:** the primary goal of the screen, the target user,
which flows matter most.

## Phase 2: Capture

### Web

```bash
node <this-skill-dir>/capture.mjs <scratchpad>/ui-audit https://<host> \
  "/,/pricing,/settings" 360,768,1440 light,dark
```

Run it from the audited repo's root so `playwright-core` or `playwright` resolves. If it
asks for a browser revision that is not downloaded, point `CHROME` at a cached Chromium
(`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`). Set `THEME_KEY` if the
site's theme is not stored under `localStorage.theme`.

It writes a full-page screenshot and the visible text for each route × width × theme, plus
`measurements.json`:

- text below the 1.25rem floor, measured against the root size (a non-16px root renders
  every class at a different pixel size)
- approximate contrast failures (solid backgrounds only)
- touch targets under 44px
- horizontal overflow and the elements that cause it
- font families and sizes in use
- unnamed controls and images without alt
- console errors

The numbers find candidates; **look at the screenshots** to judge them. Grep the `.txt`
files for copy rules.

Start at 360, the narrowest common phone. Run every theme at least at 360 on the main
routes.

**Theme polarity first.** Before judging colour, confirm each screenshot shows the theme
you asked for. A wrong theme makes every colour finding false.

### Native apps (mobile-mcp)

```
mobile_list_available_devices     → pick device
mobile_launch_app                 → open app
mobile_take_screenshot            → capture current state
mobile_list_elements_on_screen    → hierarchy, labels, touch targets
mobile_swipe_on_screen            → next screen
```

Capture the primary path, then secondary paths, then empty, loading, error and success
states, in light and dark.

## Phase 3: Audit

Check the repo rules table first. Then grade the dimensions in
[audit-dimensions.md](audit-dimensions.md), A to F each, with one line of evidence per
grade.

**The Jobs filter** — for every element:
1. Would a user need to be told this exists? Redesign until it is obvious.
2. Can it be removed without losing meaning? Remove it.
3. Does it feel inevitable? If not, it is not done.

**AI-slop check.** Flag what reads as generated rather than designed: generic gradient
heroes, three-card feature grids with icons, centred everything, emoji as icons, uniform
rounded cards, stock CTAs, filler copy that says nothing ("Ancient wisdom meets modern
technology"). If the product has a committed look, anything off that look is a finding.

## Phase 4: Triage and report

Rank by impact:
- **Critical:** broken or unreadable, or breaks a repo rule.
- **Refinement:** hurts clarity.
- **Polish.**

Mark a finding *deferred* when the fix is outside design scope or outside this repo. Put
functional bugs found on the way in the report too; they become issues, not style commits.

Write the report where the repo keeps reviews (e.g. `reviews/ui-audit-YYYYMMDD.md`):

```markdown
## Design Audit — <host>, YYYY-MM-DD

**Scope:** N routes × widths × themes. **Not checked:** [what and why]
**Assessment:** [1–2 sentences]

| Dimension | Grade | Evidence |
|---|---|---|

### Critical
- **F-01** [route @ width/theme] [issue] → [fix] → [why]. Verdict: CONFIRMED (`file.png`, measurement)

### Refinement
### Polish
### Deferred
### Not a finding
[things that looked wrong and were checked — so the next audit does not re-raise them]
```

## Phase 5: Fix (only when asked)

The audit only reports. Fix only the findings the owner approves:
- One finding per commit, `style(ui): F-NN — …`, on a branch.
- Fix at the source, with the smallest change, design scope only.
- Re-capture the same route × width × theme after each fix and attach before/after. A fix
  that cannot be shown is not done. Revert any fix that regresses another width or theme.
- Verify on the deployed preview before calling it shipped.

## Scope

**Touch:** visual design, spacing, typography, colour, motion, accessibility, UI copy.
**Don't touch:** logic, state, APIs, features, data models. If design needs a functional
change, say "This requires [change]. Flagging — outside design scope."

## Anti-patterns

| Don't | Do |
|---|---|
| "Make this blue" | "Use the accent token so the primary action reads first" |
| "Add padding" | "Raise to 16px so the groups separate" |
| "Make it pop" | "Raise contrast from 3:1 to 4.5:1" |
| "Looks fine in the code" | "Measured at 360px dark: 18px computed" |
