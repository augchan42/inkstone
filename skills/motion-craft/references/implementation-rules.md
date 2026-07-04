# Implementation Rules

## Client boundaries (React-family frameworks)

- Keep the smallest practical client boundary (`"use client"` or framework
  equivalent) around each animation island.
- Use a NORMAL import for small, immediately visible animation islands.
- Use lazy/dynamic import only where deferred loading materially reduces
  initial JavaScript (heavy or below-the-fold experiences). In Next.js,
  `ssr: false` must live inside a Client Component; dynamic import of a
  Client Component from a Server Component does not code-split automatically.
- SSR safety: no `window`/`document` access at module scope.

## Animatable properties

- DEFAULT to compositor-friendly `transform` and `opacity`.
- NEVER animate layout-affecting properties: width, height, top, left,
  right, bottom, margin, padding, font-size.
- Paint-heavy properties (SVG stroke-dash, mask, clip-path, filter, color)
  are allowed for expressive work when ALL hold: an explicit visual reason,
  a bounded surface area (one hero, not every card), mobile testing, and
  measured performance evidence in the run artifacts.

## Bundle strategy

- Detect what's installed before importing anything.
- If multiple islands share a motion library with a lazy-feature API (e.g.
  framer-motion `LazyMotion`), use it.
- Prefer CSS-only animation where the library adds no value.
- No library import for trivial hover/reveal effects — CSS handles those.
- Record the bundle-size delta (baseline production build vs changed build,
  using the repo's existing analyzer or emitted build stats).

## Accessibility

- Respect `prefers-reduced-motion` in BEHAVIOR: gate non-essential motion via
  the library hook (e.g. `useReducedMotion`) or the CSS media query. Reduced
  variant must still deliver the content (fade or none — never a blank).
- Keyboard focus must remain visible and usable through every animation.
- No autoplaying motion longer than 5s without a pause affordance.

## Internationalization

- No choreography that assumes one language's text metrics (word count,
  line breaks, string width). Verify against the target's configured locales.
- Avoid animating text reveal word-by-word for CJK/Thai content unless
  segmentation is handled correctly.

## High-volume templates

- Never add animation code to templates the policy discovery step excluded
  (programmatic/pSEO routes) unless the user explicitly included them.
- Verify exclusion: a representative generated route must receive no new
  animation bundle (check the build output or route-level JS).
