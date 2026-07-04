# Verification Gates

Two kinds of visual evidence per changed section:
- **Stable design screenshots** — animations disabled (Playwright: reduced
  motion emulation + `page.screenshot({ animations: 'disabled' })`) for
  repeatable comparison.
- **Motion evidence** — animations enabled, timed sequence or video.

Reduced motion is tested by BROWSER EMULATION
(`prefers-reduced-motion: reduce`), not by code review alone.

Run each APPLICABLE project-defined check. When a check is unavailable,
record `N/A — command/tool not present`; never record it as passed. Do not
install verification tooling without authorization.

```text
[ ] Production build succeeds
[ ] Typecheck succeeds
[ ] Lint succeeds
[ ] Existing test suite succeeds
[ ] Desktop and mobile screenshots captured
[ ] Reduced-motion browser run captured
[ ] No animation-attributed layout shifts; no material CLS regression vs baseline
[ ] No animation code added to excluded high-volume templates
[ ] Locale smoke tests pass for every configured locale
[ ] Keyboard focus remains visible and usable
[ ] Bundle-size delta recorded (baseline vs changed production build)
[ ] Console errors and hydration warnings checked
```

Store the filled checklist and evidence under
`<target_repo>/.artifacts/site-upgrade/<run-id>/<section-id>/`.
