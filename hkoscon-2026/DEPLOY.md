# Deploying the HKOSCon 2026 slide deck

The talk deck (`hkoscon-2026-talk.html` + image assets in this folder) is hosted on Vercel as a plain static site — no build step.

## Live URLs

- Public: https://hkoscon-2026-inkstone.vercel.app/
- Dashboard: https://vercel.com/augchan42s-projects/hkoscon-2026-inkstone

## How it's served (important)

- Vercel project: `hkoscon-2026-inkstone` (scope `augchan42s-projects`), `rootDirectory: null`, no framework/build.
- The deploy uploads **the contents of this `hkoscon-2026/` folder**, and the deck is served at `/` as **`index.html`**. Assets (`qr-*.png`, `*.webp`) sit at the root and are referenced by bare filename in the HTML.
- Because the source file is named `hkoscon-2026-talk.html` (not `index.html`), each deploy stages a copy named `index.html` so `/` resolves. That copy is temporary and is **not** committed to git.

## Deploy a new version (from this machine or a fresh one)

Run from the repo root. Requires `vercel` CLI logged in as `augchan42` (`vercel whoami`).

```bash
cd hkoscon-2026

# 1. Link this folder to the existing project (first time on a machine only;
#    creates a gitignored .vercel/ here — the repo root .gitignore covers it)
vercel link --yes --project hkoscon-2026-inkstone

# 2. Stage the deck as index.html so it serves at "/"
cp hkoscon-2026-talk.html index.html

# 3. Ship to production
vercel --prod --yes

# 4. Clean up the temp file (keep the working tree clean)
rm index.html
```

## Verify the deploy

```bash
u=https://hkoscon-2026-inkstone.vercel.app
curl -s "$u/" | grep -c "Support HKOSCON"   # expect 1 (patron slide present)
curl -s -o /dev/null -w "%{http_code}\n" "$u/qr-patron.png"  # expect 200
```

## Notes

- The `.vercel/` link dir is git-ignored (root `.gitignore` has `.vercel`). It only lives on machines you've linked; a new machine just re-runs step 1.
- This is **not** wired to git auto-deploy — pushing to `main` does not update the live site. You must run the steps above.
- If you'd rather drop the `index.html` copy dance, either rename the source to `index.html` and commit it, or add a `vercel.json` rewrite (`/` → `/hkoscon-2026-talk.html`) in this folder.
