# Plan Review Dimensions

Criteria for the three review lanes. When dispatching context-blind subagents, copy the relevant lane's section into the subagent prompt verbatim. When using Codex, include all three lanes as parallel agents in one prompt.

## Lane 1 — Zero-Context Executability

Role-play a skilled engineer who has never seen this codebase, executing the plan literally, top to bottom. You may read the repo only where the plan tells you to. Every moment you would have to guess is a finding.

- **Vague actions:** "Update the config appropriately", "handle errors", "refactor as needed" — flag every step without a concrete, single-interpretation action.
- **Missing exactness:** File paths without exact locations, functions without signatures, commands without exact invocations, "run the tests" without the command.
- **Unverifiable steps:** Every step should state its observable outcome ("expected: FAIL with 'function not defined'", "expected: 200 with body {...}"). Steps whose success cannot be checked are findings.
- **Hidden prerequisites:** Steps that silently depend on tools, env vars, credentials, running services, or seeded data the plan never sets up.
- **Context leaks:** Steps that only make sense if you were in the planning conversation ("as discussed", "the approach we chose", references to decisions recorded nowhere).
- **Ordering traps:** Steps that use something created by a later step; instructions whose literal order fails.

## Lane 2 — Grounding & Traceability

You have repo access and (if provided) the source spec. Verify; do not trust.

- **Path grounding:** Every file the plan says to modify — does it exist? Every file to create — does it already exist (collision)? Every referenced function/class/table/config key — is it real, with the described signature/behavior?
- **Command validity:** Are named scripts/targets present in package.json/Makefile/etc.? Do referenced test commands match the project's actual test runner?
- **Spec coverage (if a spec exists):** Walk the spec requirement by requirement — is each one implemented by some task? Uncovered requirements are critical findings.
- **No invention:** Walk the plan task by task — does each trace back to the spec (or to necessary scaffolding)? Work the spec never asked for is a finding (scope creep at plan level).
- **Constraint fidelity:** Global constraints (version floors, naming rules, platform requirements) copied from the spec — verbatim and complete? Diluted or paraphrased constraints are findings.
- **Convention conflicts:** Steps that contradict CLAUDE.md/AGENTS.md, existing ADRs, or the codebase's established patterns.

## Lane 3 — Structure & Risk

Read the plan as a tech lead deciding whether to green-light execution.

- **Task granularity:** Tasks should be the smallest unit carrying its own test cycle — flag monolith tasks ("build the backend") and confetti tasks (pure setup steps that belong inside the task needing them).
- **Dependencies:** Is the task order a valid topological sort? Could a reviewer approve task N while rejecting task N+1, or are tasks secretly entangled?
- **Interfaces between tasks:** Where task B consumes what task A produces, are the exact names/signatures/types stated? (A task implementer may see only their own task.)
- **Verification cadence:** Does each task end in a runnable check (test, build, manual verification with expected output)? Plans that defer all verification to the end are high-severity findings.
- **Test-first discipline:** Where the project follows TDD (superpowers plans always do), does each task write and run the failing test before the implementation step?
- **Failure handling:** What happens when a step fails? Any step that mutates shared state (migrations, deployments, data backfills, published APIs) needs a stated rollback or an explicit "irreversible — checkpoint first" warning.
- **Commit cadence:** Are commits frequent enough that a bad task can be reverted without unwinding good work?
- **Estimated blast radius:** Does the plan touch anything (CI, shared libs, infra) whose breakage would block others, without flagging it?

## Severity Guide

- **critical** — executing the plan as written fails or builds the wrong thing: ungrounded path/API, uncovered spec requirement, broken step ordering, irreversible step with no safeguard
- **high** — an executor must guess, and plausible guesses diverge: vague action, missing interface contract, missing verification on a risky step
- **medium** — friction: missing expected output, coarse task, late verification, undocumented prerequisite likely present anyway
- **low** — polish: wording, formatting, redundant steps

## Format-Specific Checks

**Superpowers plan** (`docs/superpowers/plans/*.md`): must have the required header (agentic-worker note, Goal, Architecture, Tech Stack, Global Constraints), tasks with Files/Interfaces blocks, checkbox (`- [ ]`) steps sized 2-5 minutes, per-task TDD cycle (failing test → verify fail → implement → verify pass → commit). Missing header sections or non-checkbox steps break the executing-plans/subagent-driven-development tooling — flag as high.

**planning-with-files** (`task_plan.md`): phases with status markers, linked `findings.md`/`progress.md`; flag phases without completion criteria.

**Kiro tasks** (`.kiro/specs/*/tasks.md`): tasks should reference requirement IDs from requirements.md — flag orphan tasks.
