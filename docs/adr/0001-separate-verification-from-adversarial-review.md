# ADR-0001: Separate implementation verification from adversarial review

- Status: Accepted
- Date: 2026-10-22
- Scope: Inkstone's engineering skills and their handoffs

## Context

Agent-generated code can outpace the attention available for human review.
Reading every changed line is not sufficient evidence that a change meets
its intent, and reducing review time can simply move effort into repairing
escaped failures.

[How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/),
published on 15 October 2026 by Addy Osmani, Morgan Westlee Lunt, and Qing
Wang, describes layered verification, automated review, risk-based human
attention, staged releases, and recovery. [Osmani's 18 October X post](https://x.com/addyosmani/status/2111604705340326393)
emphasizes runnable feedback loops and evaluating evidence when code volume
exceeds human reading capacity. Their reported improvements describe
Anthropic's environment, not measured results for Inkstone or its users.

Inkstone already has `codex-review`, used to call Codex for an adversarial
review of Opus-generated code. Folding implementation verification into
that skill would blur who produced the evidence, what was checked, and
whether an independent review actually happened.

## Decision

### Keep two distinct capabilities

- [`verify-change`](../../skills/verify-change/SKILL.md) guides the
  implementation agent through mapping intended behavior and failure modes
  to checks, running them, and producing an evidence handoff. The authoring
  agent can perform it. It does not call Codex or issue a review verdict.
- [`codex-review`](../../skills/codex-review/SKILL.md) remains the separate
  adversarial review. Its reviewer works from the resolved code scope and
  review guidance, without the implementation conversation. Verification
  results do not replace that review when it is requested or required.

When both are requested, verify the implementation before handing it off
for adversarial review. Keep the human-facing evidence record distinct
from the independent reviewer's input so the handoff does not compromise
the review's isolation. Neither skill automatically invokes the other.

[`deliver-change`](../../skills/deliver-change/SKILL.md) is the optional
orchestrator for task framing, implementation, and verification. Codex
review is off unless the user opts in; the wrapper then coordinates the
separate reviewer without passing it the author's implementation narrative.
The wrapper preserves existing authority for repairs and delivery actions
and adds no merge or deployment permission of its own.

### Make claims traceable to observable evidence

Choose checks from requirements and established contracts, with effort
proportionate to consequences of failure. Use existing tests, meaningful
reproducers, runtime interactions, and relevant invariants rather than
adding a uniform test suite to every change.

Record the tested code state, environment, command or procedure, actual
outcome, and supporting output. Distinguish passed, failed, not-run, and
blocked checks. Recheck affected behavior after edits; an earlier passing
run cannot silently become evidence for new code. Include what the checks
miss. A build, screenshot, or another model's agreement alone does not
establish all aspects of correctness.

### Preserve human decisions and recovery context

The handoff identifies residual risk and a practical recovery path for
consequential changes, distinguishing proposed recovery from tested
recovery. Humans retain product intent, judgment, and ownership under the
target project's existing rules. The new skill grants no merge authority
and changes no required reviewers, branch protection, deployment settings,
or approval thresholds.

Anthropic's internal low-risk approval paths depend on their checks,
trusted-author policy, and operational capabilities. We do not adopt those
paths as a default for repositories using Inkstone.

### Bound loops by their purpose

The article's three-round review cap addresses repeated reviewer/fixer
cycles. For implementation verification, we adopt a three-attempt
checkpoint rather than a termination cap: after three failed
repair-and-check attempts on the same behavior, the agent must summarize
the evidence and diagnose the failing assumption or choose a materially
different strategy before another attempt. It must identify what the next
check will establish; repeating the same approach without that decision
does not satisfy the checkpoint.

The agent then continues authorized repair with a new attempt count,
within the task's time, cost, and risk limits. The checkpoint itself is
neither a reason to stop nor a requirement for renewed permission. Actual
missing input or access can still block progress. Earlier diagnosis is
appropriate when retries are already uninformative; assertions must not
be weakened to make a check pass. This checkpoint is Inkstone's adaptation
of the convergence principle, not a claim that the article prescribes the
same rule for implementation repairs.

When a recurring failure exposes a stable invariant, propose a focused
regression check or project instruction. Repository-wide review services,
nightly audits, and incident-based reviewer evaluations remain separate
adoption work when requested.

## Consequences

Implementation agents provide evidence that humans can inspect without
pretending to have independently reviewed their own work. Adversarial
review can still discover defects outside the exercised behavior. Users
can choose either capability or both according to the task and project.

Evidence has a maintenance cost and blind spots. The workflow must keep
small edits cheap, surface unavailable environments honestly, and avoid
turning successful checks into blanket safety claims. It does not promise
Anthropic's throughput or revert-rate improvements.

Teams adopting a broader version of the article's process should evaluate
total human effort, including repairs, alongside revert and incident rates.
Inkstone does not collect these metrics or change approval policy through
this documentation decision.

## Alternatives considered

- **Extend `codex-review` to cover everything:** rejected because authoring
  checks and an independent review have different inputs and guarantees.
- **Rely on the implementation agent's completion statement:** rejected
  because a claim without inspectable output cannot establish behavior.
- **Mandate exhaustive manual review or a fixed test checklist for every
  edit:** rejected as the skill default; required project review still
  applies, while additional verification follows the actual failure modes.

## Implementation and validation

PR #7 adds `verify-change`, worked verification patterns, and this ADR.
The original separation left `codex-review` unchanged. The later
`deliver-change` integration makes its resolver lookup work from a
standalone installation as well as a plugin checkout. Skill validation
checks structure and references; it does not establish that future code
verified using the skill will be correct.
