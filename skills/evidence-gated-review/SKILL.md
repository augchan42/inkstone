---
name: evidence-gated-review
description: Assess whether a code change has enough verified evidence for its next review gate. Use when asked for an evidence-backed readiness check, a risk-aware review workflow, or bounded review-and-fix coordination. Wraps independent-review or codex-review; for a single diff review use that reviewer directly, and for implementation plans see plan-review-loop.
user-invocable: true
argument-hint: '[scope] [--focus "..."]'
metadata:
  version: "1.0.0"
---

# Evidence-Gated Review

Produce a decision packet for a change, not a promise that it is safe to ship.
This skill coordinates evidence and review; it does not install automation,
change repository policy, submit approvals, or authorize publication.

For provenance and the boundary between the source ideas and this workflow,
read [source and adaptation](references/source-and-adaptation.md).

## Bind the review to a snapshot

Read the target repository's instructions and applicable review policy.
Identify the requested outcome, scope, and existing authority to make changes.

Select the available Inkstone reviewer: `independent-review` if present,
otherwise `codex-review`. Read its skill and use its scope resolver; preserve
its scope, independence, and action-permission controls. Do not duplicate its
backend setup here. If neither skill or its required resolver is available,
report the missing dependency and stop rather than inventing a review command.

Record the exact base and head SHAs, resolved diff command, and path limits.
For a working-tree review, also record the dirty state and a content digest of
the reviewed patch. Include relevant untracked files in an explicit manifest with
content hashes, or state that they are excluded; a plain git diff omits them.
A manifest is not review evidence. If requested files are excluded or missed by
the selected reviewer, mark coverage incomplete until separately reviewed; do
not claim the whole worktree is ready. Do not stage files merely to hide this gap.
This is a local snapshot, not approval of a later commit.
Echo the scope before spending review effort. Stop for an empty or ambiguous
scope, and follow the reviewer's oversized-diff handling.

## Choose the evidence, not a ritual

Identify what failure would look like for this change and the smallest useful
checks for it. Prefer the project's documented commands. A documentation-only
change may need link and claim verification rather than an application build.

Keep a short evidence ledger:

| Check or claim | Snapshot | Command or inspection | Observed result | Evidence / limit |
|---|---|---|---|---|
| Regression behavior | base/head or patch digest | exact command | PASS / FAIL / NOT RUN / INCONCLUSIVE | output path, URL, or reason |
| Required CI | exact head SHA | check name and run URL | actual status | missing access is not green |

Capture exit status and relevant output for executed commands. For a proposed
test, say NOT RUN until executed; a plausible command is not evidence. For
visual work, identify the screen, viewport, and screenshot actually inspected.
Separate pre-existing failures from failures introduced by this change.

Run only checks permitted in the current environment. Pause checks requiring
unapproved credentials, writes to shared systems, or destructive setup.
Describe the gap and continue independent safe checks. Do not claim a local
subset replaces required CI or an unavailable platform.

## Route the human decision

Read available ownership rules, required checks, and approval policy. Separate
verified requirements from recommendations; if policy is inaccessible, mark
it unknown rather than inferring that no requirements exist.

Describe risk using the concrete failure mode, exposed users/data, and recovery
constraints. Use low / medium / high as discussion labels, not approval counts.
Small changes can still alter permissions, billing, persistence, or releases.

Route CI workflow changes and owner-designated sensitive paths to a human.
Escalate architectural commitments, security boundaries, or uncertain recovery
to the relevant owner. Do not treat an agent verdict as a human approval, or
count the requester as an approver without a valid applicable approval.

Never infer a trusted-author designation from ownership or familiarity.
A lighter route applies only when explicit local policy and verified author
eligibility permit it; it never removes a mandatory human gate. Track approvals
against the specific commit they cover. After a new push or conflict resolution,
re-check validity under repository policy rather than carrying approvals forward.

## Run independent review and resolve the evidence

Invoke the selected reviewer once for the resolved scope and relevant lanes.
Preserve fresh context: give reviewers the review inputs their skill permits,
not the author's reasoning or a desired verdict. Record the actual backend and
any degraded or incomplete coverage.

Use the reviewer's artifact and dispositions rather than creating a competing
finding list. Add stable finding IDs, affected file/line, supporting code or
reproduction evidence, and unresolved uncertainty where missing. Verify each
claim before accepting it; lack of a runnable reproduction is not proof that a
statically demonstrated defect is false.

Keep ACCEPTED / DECLINED / PRE-EXISTING dispositions with reasons. An accepted
finding is not necessarily fixed: separately record pending/fixed status and
the fixing snapshot. Describe recurring bug classes, but keep any fixes within
the authorized scope. Retain unresolved security findings as visible blockers.

A review request alone does not authorize fixes, issue creation, remote
comments, commits, pushes, or policy changes. Follow the selected reviewer's
permission gates and the user's current authorization before each action.

## Re-review only when it answers a question

After an authorized fix, refresh the snapshot and rerun affected checks.
A further review should verify the fix or inspect changed interactions, not
restart a broad search for old issues. Give a fresh reviewer the previous
findings and the incremental diff; inspect surrounding code when needed.

Deduplicate against prior finding IDs. Do not revive declined findings without
new evidence or silently drop unresolved ones. Do not perform several passes
by default.

Allow at most three review rounds in this invocation, including the initial
pass; parallel lanes together count as one round. If material issues remain at
that point, stop the automatic cycle and ask whether to narrow or redesign the change. Report unresolved work; the cap
is not a passing result. A required human decision or unavailable prerequisite
also stops the dependent work without suppressing its blocker.

## Deliver the readiness packet

Extend the existing review artifact, or answer in chat if no file was requested.
Recheck the target snapshot before reporting. If it changed during review,
identify the uncovered changes and mark readiness blocked until assessed.
Lead with the finding count and one verdict, in this order:
- BLOCKED: an unresolved material accepted finding, failed or missing required
  check, unknown required policy, or incomplete review prevents a decision.
- NEEDS HUMAN REVIEW: sufficient technical evidence exists, but a mandatory
  human decision or valid approval is still outstanding.
- EVIDENCE COMPLETE: the stated scope has no outstanding required gate.

A deferred pre-existing issue or advisory nit does not automatically block the
change; apply repository policy and explain the disposition. No verdict grants
merging or release authority.

Include:
- Exact reviewed snapshot and scope; any changes since it was captured.
- Findings by disposition, with unresolved accepted findings first.
- Passed, failed, missing, and inconclusive checks, linked to their evidence.
- Required human/CI gates, verified approval snapshot, and unknown policy.
- Recovery options and their limits. A revert may not undo data migrations,
  external side effects, or already-delivered behavior; do not assume rollback.
- The next action and who must decide it.

Do not merge, deploy, submit an approval, or relax checks as part of this skill.

## Improve the reviewer only when warranted

If asked to improve review quality, or a confirmed recurring miss warrants a
proposal, use an incident and its confirmed fix as a candidate test case.
Keep the expected defect separate from the review input; include a known-clean
comparison to expose harmful false positives. Compare detection and noise before
changing reviewer guidance. This is optional maintenance, not a new task for
every PR. Propose changes to project review lanes or checks; obtain authority
before editing or scheduling anything.
