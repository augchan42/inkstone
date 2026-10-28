---
name: deliver-change
description: Use when asked to deliver a development change using deepen-task and verify-change, including changes with visual deliverables. For verification alone, use verify-change; for standalone code review, use codex-review; for standalone visual criticism, use critic-loop.
---

# Deliver Change

Carry out the requested development task and hand off the result with
evidence. Coordinate the existing skills without replacing their methods
or treating a successful check as an independent review.

## Invocation and dependencies

- `deliver-change <task>`: deepen the approach, implement, and verify.
- `deliver-change --review <task>`: also run adversarial codex-review.
- `deliver-change --no-review <task>`: explicitly omit that optional stage.

These are skill invocation conventions, not a new executable CLI. A clear
natural-language request for Codex review also opts in. A routine request
to inspect the work does not silently enable a separate model run. Honor
an explicit opt-out; clarify contradictory review instructions if needed.
These flags control optional adversarial code review. Visual criticism follows
the artifact rule below, including with `--no-review`; an explicit request to
skip visual criticism controls that separate stage. Keep required project
reviews visible and resolve an explicit conflict before claiming acceptance.

Locate and read `deepen-task` and `verify-change` through skill discovery,
or their sibling directories beside this skill in an Inkstone installation.
Locate and read `codex-review` only when opted in. Resolve resources from
each skill's actual installed directory, not the target repository's cwd.
For substantial visual deliverables, also locate and read `critic-loop`.
If a dependency is unavailable, name the missing stage and continue useful
independent work; do not silently replace it or claim it ran. If review was
requested but cannot run, keep it explicitly incomplete in the handoff.

## Establish the task and authority

Work in the user's target repository. Read its guidance and inspect its
initial state. Read its review, ownership and approval policy where
available; if it cannot be read, record the policy as unknown rather than
assuming that none applies. Record the starting commit and existing local changes, then
identify the task's paths, acceptance criteria, and relevant constraints.
Preserve unrelated edits throughout implementation and review.

The task supplies the authority: implement when implementation is requested,
or stop at a plan when the user asked for a plan. Calling the wrapper alone
does not add authority to publish, merge, deploy, file issues, change global
settings, or alter approval rules. Complete explicitly authorized delivery
steps without asking for the same permission again.

For a plan-only request, deliver the plan and state that implementation,
runtime verification, and code review were not run. A review flag does not
turn a plan into code or authorize reviewing unrelated existing changes.
Existing visual references do not by themselves trigger criticism of those assets.

## Frame and implement

Apply `deepen-task` to the consequential uncertainties: missing expert work,
primary evidence, useful methods, and what would demonstrate success. Keep
this brief for straightforward fixes. Preserve the requested outcome and
artifact; do not end with a rewritten prompt when the user asked for work.

Implement within the agreed scope using the project's conventions. Apply
`verify-change` during the work, selecting meaningful checks against the
acceptance criteria rather than waiting for the end to invent tests.
Follow its three-attempt checkpoint on each repeatedly failing behavior:
diagnose or change strategy, then continue authorized repairs. The checkpoint
does not end the task or start an adversarial review loop.

Before handoff, refresh evidence affected by edits. Keep passed, failed,
blocked, and not-run checks distinct, and retain the tested code identity.
Complete any applicable visual criticism before the final handoff. Optional
code review remains a separate stage.

## Visual deliverables

When the task creates or substantially changes renders, models judged through
renders, UI appearance, game-camera captures, or other visual deliverables,
use `critic-loop` before presenting them as ready. Backend-only changes have
no visual stage. A trivial correction to previously approved work needs only
the affected check unless the project requires another critic round.

Use the skill's two-critic mode: Claude Code CLI with Opus 5.5 or a later
available Opus model, and a fresh Codex CLI critic with `gpt-6-astra` at
`ultra` reasoning effort. Honor explicit user/project reviewer settings and
provider restrictions; a backend preference alone does not reduce the critic
count. Change the pair only when a different review configuration is explicit.
Claude uses the existing Claude subscription; do not
introduce an API key, paid provider, or OpenRouter fallback. If either selected
route cannot run, report that review as incomplete rather than silently
replacing it or accepting a single-critic result.

Both critics receive the same artifact state, viewing conditions and rubric,
independently of each other and the producer's reasoning. Supply actual renders
or screenshots at the intended viewing size. Follow `critic-loop` for the
rubric-before-review, blind read, combined verdict, finding dispositions,
revisions and stop rules. Its Claude CLI reference supplies the read-only
invocation. The producer's own inspection is separate from both critic passes;
record the actual tools/models, including any shared model family.

After revisions, refresh affected renders and functional/source/export checks.
Keep visual verdicts separate from gameplay, motion, sound and performance
evidence; stills leave unobservable dimensions pending. If a dependency is
missing or a stop rule ends below acceptance, hand off the useful work with
the visual stage explicitly incomplete. Do not relax the rubric or claim readiness.

## Optional adversarial review

Use `codex-review` as a separate stage. Pass a concrete task scope through
its resolver and echo the resolved scope before review. Check that it covers
the intended changes rather than relying on bare auto-detection, which can
select only a dirty diff or the last commit. Account for task-owned new
files: untracked files are absent from an ordinary git diff. Stage or commit
them only under existing authority; otherwise report the coverage gap and
resolve the scope before claiming a complete review. Do not silently include
unrelated pre-existing edits to make a scope convenient.

Preserve the reviewer's isolation: provide the resolved diff commands and
the selected review guidance, not the implementation conversation, author
rationale, verification narrative, or expected findings. Keep the evidence
handoff for the user separate. Report the actual reviewer backend and
model. Compare the actual reviewer and author models/vendors before calling the
review cross-model or cross-vendor; the CLI name does not establish independence.
A same-model fresh-context fallback is not a cross-model review.

Triage every finding using codex-review's dispositions. Fix accepted,
in-scope defects when that falls within the user's existing implementation
authority; do not introduce another approval question for an already
authorized repair. Preserve any narrower instructions, such as review-only.
Keep pre-existing defects outside this change and do not create issues or
publish artifacts merely because a dependency lists those possible actions.

After repairs, rerun affected verification and record which code state the
review covered. Use a focused re-review of changed code when the user or
project requires it, or when a consequential repair warrants it. A review
of the earlier state does not automatically cover new edits. Do not run
repeated full-scope reviews by default or confuse the implementation
three-attempt checkpoint with a review-round policy.

## Final handoff

Report the implemented outcome, tested code state, meaningful evidence,
remaining gaps, and recovery notes for consequential changes. Name any
change to CI workflows or owner-designated sensitive paths as needing a
human decision. For applicable visuals, report each critic, reviewed artifact
state, combined verdict, records, pending dimensions and unresolved findings.
Report a skipped visual stage and its reason. Add optional code
review status: not requested, incomplete, or completed, with reviewer
backend, reviewed state, finding dispositions, and any later edits it
does not cover. Keep the report proportionate to the change.

If the user requested a PR, merge, or deployment, complete that authorized
step after the applicable checks and project requirements are satisfied.
Otherwise finish with the requested artifact and handoff. Never equate the
wrapper's completion with a blanket safety claim or merge approval.
