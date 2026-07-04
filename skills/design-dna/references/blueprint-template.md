# Blueprint Template

Copy this file to `<target_repo>/design-dna/<ref-slug>.md` and fill it in.
Section headings and Motion DNA columns are a parsing contract — do not rename.

```markdown
---
schema_version: 1
source_url: https://example.com
resolved_source_url: https://www.example.com   # after redirects
captured_at: YYYY-MM-DD
run_id: YYYY-MM-DDTHH:MM:SSZ
target_repo_commit: <short-sha or "n/a">
viewports: [390x844, 1440x900]
toolchain:
  browser: <e.g. playwright-chromium 1.x / gstack-browse>
  viewport_engine: <engine + version if known>
confidence: high | medium | low
---

# <Site name> — Design DNA

## Identity
Vibe in 2–4 sentences. If chosen by research mode, include selection rationale.

## Typography
Families (role: display/body/mono), weights in use, type scale (px or rem
ladder), line-height rhythm, letter-spacing quirks, casing conventions.

## Color
Token table: background(s), surface(s), primary text, secondary text,
accent(s), borders. Include hex values and where each is used. Note
light/dark behavior.

## Spacing & Layout
Base unit, section padding rhythm, container max-widths, grid columns,
notable ratios (hero height, image aspect ratios), alignment habits.

## Imagery
Treatment (photography/illustration/3D), color grading, borders/frames,
texture/grain, how images meet text.

## Components
Recurring patterns worth abstracting: nav, hero, cards, footers, buttons,
dividers. One line each — what makes it distinctive.

## Motion DNA

| Element/pattern | Trigger | Initial state | Final state | Scroll range/threshold | Duration | Delay/stagger | Easing | Scrubbed or discrete | Mobile variation | Reduced-motion fallback | Evidence | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

Evidence ∈ extracted | runtime-observed | visually-inferred | unknown.
One row per distinct pattern, not per instance.

## Do-not-mix / cautions
Combinations observed to clash, or patterns that only work with this site's
content density.
```
