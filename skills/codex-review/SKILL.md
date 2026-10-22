---
name: codex-review
description: Run an independent code review of any git scope — uncommitted changes, a commit range, a merge commit, a PR, or specific paths — via Codex CLI, opencode, or context-blind subagents, then triage every finding with an explicit disposition. Use when asked to "review this diff", "codex review", "review PR N", "review the merge commit", or to get a second opinion on changes before or after merge. For reviewing implementation plans rather than code, see plan-review-loop.
user-invocable: true
argument-hint: "[scope] [paths] [--focus \"...\"] [--holistic] [--commit <sha>] [--pr <n>]"
metadata:
  version: "1.3.0"
---

# Codex Review

An independent code review of a **scope you choose**, not a scope some tool chose for you.

**Core principle:** the reviewer must not have seen the conversation that produced the
code. Its value is that it does not already believe the change is correct. Preserve
that — never hand it your reasoning, only the diff.

**No hook, no state file, no loop.** This skill runs start-to-finish inside one
invocation. Nothing can wedge a session, and nothing needs cancelling.

## Lifecycle

```
resolve scope → assemble lanes → run reviewer → triage findings → act
```

---

## Phase 1 — Resolve the scope

Run the resolver and use its output. Do not construct a `git diff` by hand.

Locate the directory containing this `SKILL.md` using skill discovery.
The resolver is `scripts/resolve-scope.sh` inside that directory, and
`review-lanes.md` is beside this file. Use those installed paths while
keeping the working directory in the repository being reviewed. Do not
assume that repository contains an Inkstone checkout or a `skills/` folder.

```bash
bash "<absolute installed codex-review directory>/scripts/resolve-scope.sh" <args>
```

Substitute the discovered skill directory before running the command.
For a plugin install it is normally under `${CLAUDE_PLUGIN_ROOT}/skills/`;
for a standalone install use the skill's actual location. On Windows use
an available Bash runtime such as Git Bash or WSL, with a path it can read.

Pass the user's scope arguments through unchanged, minus `--focus` and `--holistic`
(those are yours, not the resolver's). It emits `SCOPE_LABEL`, `DIFF_ARGS`,
`PATHSPEC`, `REF_SHA`, `CHANGED_FILES`, `CHANGED_LINES`, `OVERSIZED`.

| The user says | Resolves to |
|---|---|
| *nothing* | dirty tree → `git diff HEAD`; else branch vs merge-base with the default branch; else the last commit |
| `HEAD~3` | everything since that ref |
| `<sha> <sha>` or `a..b` | that range |
| a **merge commit** sha | `git diff <sha>^1 <sha>` — detected automatically |
| `--commit <sha>` | that one commit alone |
| `--pr 140` | the PR's base..head (needs `gh`) |
| `--staged` / `--uncommitted` | index / working tree |
| trailing paths | pathspec-limits any of the above |

**Echo `SCOPE_LABEL` to the user before running the review.** A review of the wrong
range is worse than no review, because it reads as clean.

**If `OVERSIZED=true`** (default threshold 2000 changed lines): say so, and offer to
split by directory rather than proceeding. A reviewer given more than it will read
carefully returns confident shallow findings.

**If the resolver warns of an empty scope**, stop and resolve that first — it is
almost always a reversed range or an over-narrow pathspec.

## Phase 2 — Assemble the lanes

Read `review-lanes.md` (in this skill's directory) and select:

1. **Core lanes** — always.
2. **Detected lanes** — run the detection checks against the target repo.
3. **Project lanes** — if `.claude/code-review-lanes.md` exists in the target repo,
   include its contents verbatim. Read it; do not summarize it.
4. **Focus lane** — from `--focus "..."`, if given.
5. **Holistic lane** — only with `--holistic`.

If a `--focus` was not given but the diff touches something whose correctness depends
on a convention rather than a type (an index base, a unit, an ordering, a locale key),
name it explicitly in the prompt anyway. That class of bug is invisible to a generic
reviewer and obvious to a primed one.

## Phase 3 — Run the reviewer

Read `reviewer-backends.md`, beside this file in the installed skill directory, and
pick the first backend that is installed, has quota, and passes its short smoke
test: **Codex CLI**, then **opencode**, then **context-blind subagents**, unless the user
explicitly selected a backend or model. Log which one
ran and why the earlier ones were skipped. The mechanics — the `< /dev/null` rule,
artifact write permissions, liveness probes, the `tail`/`head` buffering trap, the guard loop —
all live in that file; do not improvise them here.

Run the reviewer **in the background** so its output stays visible and it can be
killed if it stalls. The prompt must contain, in this order:

1. The exact diff command: `git diff <DIFF_ARGS> [-- <PATHSPEC>]`, and an instruction
   to review **only** its output first. Codex runs it; for the shell-disabled OpenCode
   agent, materialize that exact diff beforehand and supply the saved file to read.
2. `SCOPE_LABEL`, so the reviewer knows what it is looking at.
3. One block per selected lane, each ending with the finding format.
4. A consolidation instruction: dedupe overlapping findings, order by severity, and
   produce the complete Markdown artifact at the designated path using the backend's
   output contract. Include the Phase 4 format and backend/model metadata in the prompt.

Per finding: `file:line`, severity (critical/high/medium/low), lane, what is wrong,
why it is wrong, and a concrete fix.

Choose the Phase 4 artifact path before dispatch. Codex saves its final Markdown
through `--output-last-message`; OpenCode writes through its report-scoped file tool.
Confirm the artifact exists, is nonempty and matches the reviewed scope before triage.
The caller adds dispositions after reading the review; it does not invent findings.

**Don't wait idle.** The pass is long enough to run the diff's own cheap checks
alongside it — linters, localization or script guards, a targeted test suite.

## Phase 4 — Validate the reviewer-written artifact

Require the reviewer to write `reviews/review-<YYYYMMDD-HHMMSS>-<REF_SHA>.md`:

```markdown
---
scope: <SCOPE_LABEL>
diff: git diff <DIFF_ARGS> [-- <PATHSPEC>]
files_changed: <n>
lines_changed: <n>
lanes: correctness, contracts, tests, security, nextjs, project(.claude/code-review-lanes.md), focus
reviewer: "<tool (model[, agent])> — <why earlier backends were skipped, if any>"
reviewed_at: <ISO 8601>
---

## Findings

### [critical] <one-line title>
**Where:** `path/to/file.ts:142` · **Lane:** correctness
<what is wrong, why, and the fix>

...

## Verification limitations

<checks the reviewer could not perform>

## Verdict

<ready | needs revision>
```

The reviewer stops after the verdict. The caller appends `## Disposition` in Phase 5.

Recording the exact diff command in the frontmatter is not decoration — it is the only
way anyone later can tell what this review did and did not look at.

## Phase 5 — Triage

**Judge every finding yourself.** The reviewer has no context and will be confidently
wrong about deliberate decisions. Verify each claim against the code before accepting
it, and reject the ones that are wrong — a review you agree with entirely is a review
you did not actually read.

Every finding gets exactly one disposition line under `## Disposition`:

- **ACCEPTED** — real, in scope. Fix it.
- **DECLINED** — with the reason. "Deliberate: adjust-during-render is the documented
  React pattern here" is a disposition. Silence is not.
- **PRE-EXISTING** — real, but not caused by this diff. Do not fix it here; that is
  scope creep wearing a helpful hat.

```markdown
## Disposition
- [high] HexagramLines off-by-one on changingLines — ACCEPTED, fixed in <sha>
- [med] bg-accent hardcoded in HexagramDisplay — PRE-EXISTING, filed #212
- [low] extract the combobox into a hook — DECLINED: churn exceeds the value
```

## Phase 6 — Act

**Ask before doing any of these.** This skill reviews; it does not unilaterally
rewrite or publish.

1. **Fix accepted findings** — as follow-up commits, one logical fix per commit.
   Reference the review file in the commit message.
2. **File the rest** — declined-but-real and pre-existing findings become
   `gh issue create` calls, so they survive outside a markdown file nobody reopens.
   Do not fix pre-existing findings in this change.
3. **Commit the review artifact** if the project tracks `reviews/` (check whether the
   directory is in git — many projects gitignore it).
4. **Feed the lesson back.** When a finding was real and would recur, propose adding
   it to `.claude/code-review-lanes.md`. That file is how the review gets sharper each
   time instead of repeating the same generic checks forever.

## Rules

- Echo the resolved scope before reviewing. Always.
- Never `codex exec review` with a custom prompt — it will be rejected.
- Never let the reviewer see your reasoning about the change.
- Never fix pre-existing findings inside the change under review.
- Every finding gets a disposition, including the ones you reject.
- Run the reviewer backgrounded so it can be watched and killed — and never through
  `tail`/`head`, which buffer to EOF and leave the output file empty for the whole run.
- A watcher that produced no output is a broken watcher until proven otherwise.
- Always `< /dev/null` on `codex exec` and `opencode run`; without it a backgrounded run
  blocks on stdin forever, looking exactly like a slow review.
- Run OpenCode with the dedicated report-scoped agent and effective policy defined in
  `reviewer-backends.md`; reviewers may write findings but may not edit reviewed source.
- Record the reviewer as tool **and** model, and say when it was same-model.
- On any tooling failure, report it and continue degraded — never leave the user
  unsure whether a review ran.
