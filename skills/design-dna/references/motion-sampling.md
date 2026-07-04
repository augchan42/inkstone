# Motion Sampling Procedures

Run AFTER layout sampling, in the same clean browser context.

## 1. Runtime animation inventory

At initial load and again after scrolling to each major section, evaluate:

```js
document.getAnimations().map(a => ({
  target: a.effect?.target?.tagName + '.' + (a.effect?.target?.className || ''),
  keyframes: a.effect?.getKeyframes?.().map(k => ({...k})),
  timing: a.effect?.getComputedTiming?.(),
  playState: a.playState,
}))
```

Record each entry's keyframes, duration, easing, play state → evidence label
`runtime-observed`.

## 2. Four-phase scroll-trigger capture

For each element that appears to animate on entry, capture screenshots:
1. immediately before entry (element just below fold)
2. early transition (~20% through)
3. midpoint
4. settled state

Scroll in small increments (e.g. 200px steps with 300ms settle) to catch the
trigger. Evidence label: `visually-inferred` unless corroborated by step 1.

## 3. Slow-scroll trace

One controlled slow scroll top-to-bottom per viewport (desktop 1440×900,
mobile 390×844), captured as video/trace if the tooling supports it,
otherwise a dense screenshot series (every 400px). Store under
`.artifacts/site-upgrade/<run-id>/<ref-slug>/`.

## 4. Interaction states

Exercise and capture: hover on nav/buttons/cards; keyboard focus (Tab
through the header and one card grid); navigation open; one
accordion/modal if present; one route transition if the site is a SPA.

Use a real UI click, not a synthetic `element.click()` dispatched from
injected JS — portal-rendered menus/sheets/dialogs (common in component
libraries like Radix/shadcn) frequently only open in response to a
trusted pointer event and will silently no-op otherwise.

## 5. Scrubbed vs discrete

An animation is *scrubbed* if reversing scroll direction reverses the
animation mid-flight; *discrete* if it plays to completion once triggered.
Test by scrolling down 200px past a trigger, then up. Record per pattern.

## Recording rules

- Every observation gets exactly one evidence label.
- When code inspection and visual capture disagree, prefer runtime evidence
  and note the disagreement.
- Unknowns are recorded as `unknown`, never guessed.
