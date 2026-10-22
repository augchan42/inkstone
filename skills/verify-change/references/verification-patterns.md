# Verification Patterns and Source Analysis

Use the relevant pattern rather than running every example. These examples
describe desired behavior; no checks in them have actually been run.

## Denied access: a small diff with consequential risk

**Change:** An endpoint should allow a user to update their own record but
deny updates to another user's record.

**Useful evidence:** An isolated integration test exercises the real route
with two users and verifies both the status and the stored record after the
denied request. Include an unauthenticated case if the route contract
requires authentication. Use fixtures rather than another person's live data.

**Weak evidence:** A unit test of a helper that compares user IDs while the
route never calls that helper. Type checking does not establish authorization.

**Handoff:** Name which roles and boundaries were exercised and whether
the real database adapter was used. A two-line fix can still deserve
careful human review under the project's policy.

## UI action: distinguish appearance from behavior

**Change:** A save button persists an edited display name.

**Useful evidence:** In a test environment, edit the name, click Save,
observe the completed request or equivalent persisted state, reload, and
verify the value remains. Check the failure state if error handling changed.
Capture the relevant rendered state when visual layout is part of the change.

**Weak evidence:** A screenshot of the button, a successful build, or a toast
that appears before persistence succeeds. None establishes that Save works.

**Handoff:** If only component tests were possible, state that the browser
flow and real persistence were not exercised. Do not label the feature
verified end to end.

## Data transformation: choose an independent expectation

**Change:** Convert local schedule entries to UTC without changing their
meaning around a daylight-saving transition.

**Useful evidence:** Compare selected known instants to an authoritative
timezone reference for the supported zones. Test meaningful invariants,
including the application's explicit policy for ambiguous or nonexistent
local times. Round-trip checks can supplement known-answer cases.

**Weak evidence:** Implementing both conversion directions with the same
wrong offset and showing they round-trip. Two functions can agree while
both are wrong. A generated expected-output snapshot can have the same flaw.

**Handoff:** Record the timezone database/runtime version where relevant
and the zones and transition cases tested. Do not imply every zone passed.

## Small copy correction: keep verification proportionate

**Change:** Correct a typo in static help text.

**Useful evidence:** Inspect the source diff, preserve links and markup,
and use existing documentation checks if the project requires them. Check
the rendered text if the edit affects wrapping or layout.

**Weak process:** Creating a new E2E suite or adversarial code-review loop
solely to prove the spelling correction. More checks can cost attention
without addressing a meaningful failure mode.

## Evidence goes stale

If tests passed on commit A and a subsequent edit changes persistence on
commit B, refresh the persistence checks. An unchanged typography check
may remain useful if its relevant inputs did not change. Record the reason
for carrying evidence forward rather than silently relabeling it as a run
against B. If the relationship is unclear, mark the check not run for B.

## Three failed repairs: checkpoint and continue

If three repair-and-check attempts still leave Save failing to persist a
name, summarize the attempted repairs and observed failures before attempt
four. Diagnose a concrete assumption, such as a component test bypassing
the real route, or change strategy, such as tracing the isolated request
through the persistence adapter. State which next check will distinguish
the suspected cause. Continue the authorized repair and begin a new count.
Reaching three alone does not end the task or require new permission.

## Relationship to other Inkstone skills

- **verify-change:** The implementation agent demonstrates intended
  behavior and reports evidence, blind spots, and a recovery path.
- **codex-review:** Calls Codex for an adversarial review of Opus-generated
  code. It looks for defects beyond what the implementation agent checked.
  A passing verification handoff cannot replace this review when requested.
- **plan-review-loop:** Challenges an implementation plan before execution.
  Verification here examines an implemented change.

The verification record can accompany a review or PR. Do not feed the
implementation conversation to an independent reviewer or change its
review instructions under the guise of this handoff.

## Sources and interpretation

The strongest recent X match found for this request was
[Addy Osmani's 18 October 2026 post](https://x.com/addyosmani/status/2111604705340326393).
His profile identifies his work as Claude Code at Anthropic. The post
addresses the mismatch between code production and human reading capacity
and recommends runnable feedback loops, risk assessment, and evaluation of
evidence. It mentions E2E tests, property tests, feature maps, and
adversarial reviews. The compact behavior-to-check map in this skill is a
local adaptation, not a claim to reproduce a separate feature-map specification.

The linked primary article,
[How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/),
was published 15 October 2026 by Addy Osmani, Morgan Westlee Lunt, and Qing
Wang. Both sources were read using Browser on 22 October 2026.

The article describes a broader team system: local verification,
automated and human review, CI, staged releases, and recovery. Its useful
criterion is total human effort, including fixing escaped failures;
reducing review time alone can hide a transfer of cost into incidents.
It also discusses preserving team understanding through targeted
explainers and bounding review loops that keep rediscovering old findings.

This skill deliberately extracts one reusable practice: make the agent
produce inspectable evidence before handoff. It does not recreate the
review service or adopt Anthropic's internal approval tiers. The source's
reported throughput and revert improvements describe their environment;
they do not establish that this skill will produce the same results in
another repository.
