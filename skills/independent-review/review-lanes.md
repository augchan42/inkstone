# Review Lanes

A lane is one reviewer with one job. Lanes run in parallel and their findings are
deduplicated afterward. Fewer, sharper lanes beat many broad ones — a reviewer told
to check everything reports mostly noise.

Lane selection per run:

1. **Core lanes** — always on (below).
2. **Detected lanes** — added when the stack is detected in the target repo.
3. **Project lanes** — read verbatim from `.claude/code-review-lanes.md` in the target repo.
4. **Focus lane** — built from the `--focus "..."` argument.
5. **Holistic lane** — only with `--holistic`.

---

## Core lanes (always on)

### Lane: Correctness

The changed code, judged against what it is trying to do. Not style.

- Off-by-one and boundary errors — especially where the diff introduces or consumes an
  index whose base or direction is a convention rather than a type (1-indexed vs
  0-indexed, bottom-to-top vs top-to-bottom, inclusive vs exclusive ends). A wrong
  convention here produces plausible-looking output, which is why it survives review.
- Null/undefined/empty paths through new branches.
- State that is read after it is mutated, or mutated during render.
- Effects: missing cleanup, wrong dependency arrays, effects doing work that belongs
  in an event handler.
- Async: unawaited promises, races between concurrent writers, error paths that
  swallow rejections.
- Error handling that catches too broadly or reports too little.

### Lane: Contracts & call sites

New or changed interfaces, and everyone who uses them.

- Every caller of a changed signature updated? Search for them; do not assume.
- Props/parameters whose meaning is carried by a name rather than a type — document
  the convention at the definition, and verify each call site honors it.
- Removed exports, keys, or config values: is every consumer gone too?
- Data that crosses a boundary (server→client, API→UI, prompt→parser): does the
  producer's shape still match the consumer's expectation?

### Lane: Tests

- Does each new behavior have a test that would fail without the change?
- For a bug fix: is there a regression test that reproduces the original bug?
- Edge cases: empty, null, boundary, error path.
- Do the tests assert behavior, or do they assert implementation details that will
  break on the next refactor?
- Are new tests deterministic and isolated (no shared mutable state, no real clock,
  no network)?

### Lane: Security

Scoped to the diff, not the whole codebase.

- Input validation and sanitization on anything user-supplied.
- Authorization checks on new routes, actions, and mutations — treat a server action
  as a public endpoint.
- Injection surfaces: SQL, shell, path traversal, XSS via unescaped interpolation.
- Secrets: hardcoded credentials, tokens in logs, keys committed to the tree.
- Error messages that leak internals to users.

### Lane: Simplification

Findings here are advisory by default — flag, do not demand.

- Copy-pasted blocks that should be one function.
- Abstractions introduced for a single caller.
- Dead code and unreachable branches left by the change.
- Complexity that a smaller data structure would remove.

---

## Detected lanes

Add a lane when the marker is present in the target repo.

| Lane | Detection |
|---|---|
| Next.js / React | `next.config.*` or `"next"` in `package.json` |
| Browser UI / a11y | `app/`, `pages/`, `src/app/`, `src/pages/`, `public/`, or `index.html` |
| iOS / SwiftUI | `*.xcodeproj`, `Package.swift`, or `*.swift` in the diff |
| Database / migrations | migration directories, `*.sql` in the diff |

### Lane: Next.js & React

- Server Components by default; `'use client'` only where interactivity requires it.
- Data fetched in Server Components, not effects.
- `params`/`searchParams` awaited as Promises.
- Cache strategy explicit and correct; `revalidateTag`/`revalidatePath` after mutations.
- Server Actions validated and auth-checked.
- Derived state computed during render, not synced via effects.
- No barrel-file imports; heavy client-only components behind `next/dynamic`.

### Lane: Browser UI & accessibility

- Keyboard operability of anything newly interactive; visible focus indicators.
- Correct roles and ARIA for composite widgets (combobox, listbox, dialog, tabs) —
  and `aria-activedescendant`/`aria-expanded` kept in sync with actual state.
- Color contrast on new or changed tokens.
- Touch target size; layout at small widths.
- Loading, empty, and error states for anything that can be slow or fail.

### Lane: Design tokens & theming

Add this lane whenever the diff touches a color, spacing, or typography token — this
is the classic "looked fine in the theme I was using" defect.

- Every changed token verified in **every** theme the project ships, not just the default.
- Semantic tokens used rather than raw values.
- Contrast re-checked per theme, not once.

---

## Project lanes

If `.claude/code-review-lanes.md` exists in the target repo, include its contents
verbatim as additional lanes. That file is where a project records the invariants
that have actually bitten it — the ADR its code must not violate, the token that
broke twice, the mobile constraint that regresses. It is maintained by the project,
not by this skill.

Suggested shape:

```markdown
# Code review lanes — <project>

## Standing invariants
- <rule that has been violated before, and what to check>
- <ADR number and the constraint it imposes>

## Known traps
- <the thing that looks correct but is not>
```

## Focus lane

Built from `--focus "..."`. Diff-specific emphasis that is not worth recording
permanently — "the new `changingLines` prop is 1-indexed bottom-to-top", "I removed
nine i18n keys, check nothing still references them". Passed to the reviewer as its
own lane so it is not diluted by the generic criteria.

## Holistic lane (`--holistic` only)

Whole-project structure: module boundaries, god files, dependency cycles, config
sprawl, agent-harness docs (`AGENTS.md`/`CLAUDE.md` coverage), observability.

Off by default on purpose. It reports on code the diff never touched, which
produces long reviews whose findings are all out of scope for the change under
review. Run it deliberately, on its own, not bundled with a diff review.
