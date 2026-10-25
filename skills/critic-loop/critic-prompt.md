# Critic prompt

Fill the brackets. Send part A first; send part B only after the critic has answered
part A. With a one-shot backend (Codex CLI, opencode), run part A as its own call and
part B as a second fresh call that includes part A's answer — the critic in part B
then sees the brief, but its blind read was already fixed before it did.

## Part A — blind read

```
You are an independent critic. You have not seen how this work was made and you are not
told what it is meant to show.

Look at the attached [image(s) / text]. They will be seen [viewing condition, e.g. "on a
phone, about 360 px wide" / "as a 120 x 53 character canvas"].

Answer only this, in three short lines:
1. Subject: what is shown (or said), as a stranger would name it.
2. Action: what is happening, if anything.
3. Unclear: anything you cannot make out.

Do not guess at intent. If you cannot name the subject, say so.
```

## Part B — scored verdict

```
You are an independent critic. Your blind read of this work was:
[part A answer]

Now the brief: [the brief from the rubric, with the owner's standing taste and past verdicts if any].

Rubric (total 10):
[categories, maximum scores and what full marks means]

Blocking conditions:
[list]

[Round 2+: The previous round's work is attached as [file] and its verdict follows.
What changed since then: [one line per change].
[previous verdict]]

Write the verdict in this form:

## Blind read vs brief
Match / partial / no match, and why.

## Scores
- [Category] [n]/[max] — gaps: [every gap that keeps it from full marks, each specific
  enough to act on: where it is and what is wrong]
…
**Total:** [n]/10

## Blocking
[each blocking condition that applies, or "none"]

## Verdict
PASS | REVISE | RETHINK — [one line; for RETHINK, what to change in the approach]

Rules: be exact and do not soften. A regression scores lower than the previous round.
Stay consistent with the previous verdict but you are not bound to match or raise its
score. Ignore preferences that do not affect the brief. Stop after the verdict.
```
