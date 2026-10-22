# Reviewer backends

Shared by `codex-review` (code) and `plan-review-loop` (plans). The skill decides
*what* to review and how to triage; this file decides *who* reviews it. The skill's name
is historical: Codex is the preferred backend, not the only one.

**The backend is incidental. The independence is the point.** A backend qualifies if it
has not seen the conversation that produced the change. Try them in this order and
**log which one actually ran and why the earlier ones were skipped** — a silent fallback
hides a fixable problem (on 2026-09-15 a Codex "quota failure" was a stdin deadlock).

An explicitly requested backend or model overrides the default order. If it cannot
run, report that requested review as incomplete; do not silently substitute another
model. Cross-model or cross-vendor status depends on the actual reviewer and author
models, not the CLI name.

| # | Backend | Independence | When it is skipped |
|---|---|---|---|
| 1 | Codex CLI (`codex exec`) | compare its model/vendor with the author's | `codex` missing, quota exhausted, or dead after the liveness probe |
| 2 | opencode (`opencode run`) | depends on `-m` versus the author model | `opencode` missing, no model with quota, or required permissions unavailable |
| 3 | Context-blind subagents | normally **same model** — weaker; record actual identity | either tool restriction or final-message capture is unavailable |

Record the result in the artifact frontmatter as tool **and** model, never the tool alone:

```
reviewer: "codex-cli (gpt-5.x)"
reviewer: "opencode (opencode/muse-spark-1.3-contributor-free, agent inkstone-reviewer) — codex: quota exhausted"
reviewer: "subagents (claude-fable-5-1, same-model) — codex: not installed; opencode: not installed"
```

A free or small model is a legitimate backend, but a reader deciding how much to trust
the review needs to see which one it was.

## Output contract

Before dispatch, choose a fresh absolute `REVIEW_FILE` under the target repo's
`reviews/` directory and create its parent. Resolve the real parent path; reject
symlinks and an existing output file so a stale artifact cannot count as success.
Give the reviewer the output path, artifact format, exact scope and repo root.
Reviewers write findings; they do not repair implementation files or the target plan.
The caller reads the artifact and adds dispositions afterwards.

Create a private per-attempt run directory with `mktemp -d`. Set fresh `PID_FILE`
and `EXIT_FILE` paths inside it; do not reuse status files from an earlier backend
or confirmation attempt. Keep these caller-owned files out of reviewer write access.

Before dispatch, record a source baseline: `git rev-parse HEAD`,
`git ls-files --stage -z`, `git status --porcelain=v1 -z --untracked-files=all`,
and a SHA-256 hash of `git diff HEAD --binary --no-ext-diff --no-textconv`.
Also hash the contents of each task-owned untracked input and the target plan/spec,
including ignored or external inputs when applicable. Repeat and compare after
the run. Exclude only the exact assigned report paths and caller-created logs,
config and input artifacts; do not exclude the whole `reviews/` directory or assume
a clean working tree. Record any unrelated edits already present in the baseline.

Keep logs separate from the findings file. A backend succeeds only when it exits
successfully and the assigned artifact is nonempty and contains the requested
scope, findings (or an explicit no-findings verdict), and backend/model identity.
Check that the reviewed source state is unchanged before accepting it. An empty,
missing or malformed artifact is a backend failure; log it and try the next backend.
If a failed attempt left an artifact, preserve it under a distinct failed-attempt
filename before retrying so the next backend still receives a fresh output path.
Never synthesize findings to satisfy a hook or treat a run log as a review.
Unexpected source or index changes invalidate the review. Preserve the evidence
and report the difference; do not reset a user's working tree to conceal it.

---

## Backend 1 — Codex CLI

**Never use `codex exec review`.** That subcommand rejects a custom prompt, which makes
lanes and focus impossible. Always use plain `codex exec`.

Ensure multi-agent is enabled (idempotent):

```bash
CODEX_CONFIG="${HOME}/.codex/config.toml" && if [ ! -f "$CODEX_CONFIG" ]; then mkdir -p "${HOME}/.codex" && printf '[features]\nmulti_agent = true\n' > "$CODEX_CONFIG" && echo "Created ~/.codex/config.toml with multi_agent enabled"; elif ! grep -qE '^\s*multi_agent\s*=\s*true' "$CODEX_CONFIG"; then if grep -qE '^\[features\]' "$CODEX_CONFIG"; then if [ "$(uname)" = "Darwin" ]; then sed -i '' '/^\[features\]/a\'$'\n''multi_agent = true' "$CODEX_CONFIG"; else sed -i '/^\[features\]/a multi_agent = true' "$CODEX_CONFIG"; fi; else printf '\n[features]\nmulti_agent = true\n' >> "$CODEX_CONFIG"; fi && echo "Enabled multi_agent in ~/.codex/config.toml"; else echo "Codex multi-agent: already enabled"; fi
```

Run it **in the background** (`run_in_background: true`). Keep model-generated commands
read-only and let the reviewer CLI save its final Markdown with `--output-last-message`:

```bash
codex --sandbox read-only exec --output-last-message "$REVIEW_FILE" "<prompt>" < /dev/null
```

The prompt requests the complete review as the final message, including the artifact
metadata; it must not ask the model to write the file through shell or edit tools.
`--output-last-message` is a CLI output writer, outside the sandbox applied to model
commands. This allows reviewer-written findings without source-write access. See the
[official output documentation](https://learn.chatgpt.com/docs/non-interactive-mode).

**The `< /dev/null` is not optional.** Without it `codex exec` prints
`Reading additional input from stdin...` and blocks forever: backgrounded, its stdin is
an open pipe that never reaches EOF. The tell is a process that has burned **~0.05 s of
CPU over half an hour** and has written no rollout under
`~/.codex/sessions/<yyyy>/<mm>/<dd>/`. It looks exactly like a long review and is a
deadlock before the first token — and it is easy to misread as a quota failure. Smoke
test before concluding anything about a slow pass:

```bash
codex --sandbox read-only exec "Reply with exactly: SMOKE OK" < /dev/null
```

**Quota.** A real quota exhaustion prints an error and exits; it does not hang. If the
smoke test itself fails with a usage-limit message, move to backend 2 and log it.

### Liveness, not existence

`pgrep` finding the process proves nothing — a deadlocked Codex is still a process.

```bash
ps -o etime=,time= -p <pid>                       # elapsed vs CPU time consumed
ls -t ~/.codex/sessions/$(date +%Y/%m/%d)/*.jsonl # a live run writes a rollout within seconds
```

Probe at ~90 s: no rollout file → dead on arrival; kill it, log
`backend=codex DEAD (no rollout within 90s)`, fall through. Hard cap ~15 minutes; a run
log unchanged for 5 consecutive minutes is a hang.

---

## Backend 2 — opencode

Works non-interactively. Pick a model with quota (`opencode models` lists them; the
`opencode/*-free` entries cost nothing and are fine for a review, just record which one).

Use a dedicated **`inkstone-reviewer`** agent, not the built-in `plan` or `build`
agent. Plan is not a filesystem sandbox: shell commands follow inherited permissions
and configuration can override edit restrictions. This backend instead disables shell,
delegation and unspecified tools, and allows edits only to the assigned report.

Run from the target repository's Git worktree root. For OpenCode v1, generate a
temporary JSON config with this shape, substituting the exact report path relative
to that worktree using a JSON serializer, not shell string interpolation:

```json
{
  "formatter": false,
  "lsp": false,
  "agent": {
    "inkstone-reviewer": {
      "description": "Review source and write only the assigned findings artifact",
      "mode": "primary",
      "permission": {
        "*": "deny",
        "read": {
          "*": "allow",
          "../*": "deny",
          "../../private-review-input/scope.patch": "allow"
        },
        "glob": "allow",
        "grep": "allow",
        "list": "allow",
        "external_directory": {
          "*": "deny",
          "/absolute/private-review-input/*": "allow"
        },
        "edit": {
          "*": "deny",
          "reviews/assigned-review.md": "allow"
        },
        "bash": "deny",
        "shell": "deny",
        "task": "deny",
        "subagent": "deny"
      }
    }
  }
}
```

Keep `REVIEW_FILE` absolute in the prompt. OpenCode v1.18.34's write tool checks
`edit` permissions against a worktree-relative resource, so an absolute allow rule
does not match it. Derive the relative rule from the canonical output path and the
actual worktree root; do not add a wildcard prefix to make it match. See the
[write-tool implementation](https://github.com/anomalyco/opencode/blob/v1.18.34/packages/opencode/src/tool/write.ts).

Create the input directory with `mktemp -d`, not a predictable shared name, and put
only the materialized diff or copied external plan/spec inputs there. Generate its
absolute directory allow rule and exact worktree-relative `read` exceptions using
the actual paths. An `external_directory` check uses a directory marker ending in
`/*`, not the individual filename; the `read` exception permits only the named input.
See the [external-directory implementation](https://github.com/anomalyco/opencode/blob/v1.18.34/packages/opencode/src/tool/external-directory.ts)
and [read-tool implementation](https://github.com/anomalyco/opencode/blob/v1.18.34/packages/opencode/src/tool/read.ts).
Do not grant access to the whole home directory or other repositories. For a plan
with no external inputs, omit the exceptions and deny all external directories.

Keep `formatter` and `lsp` disabled in this per-run config: file reads/writes can
otherwise start configured processes outside the shell tool's permission gate.

Apply it per invocation through `OPENCODE_CONFIG_CONTENT`; do not change global or
project settings. With the same inline config and `--pure`, inspect
`opencode debug agent inkstone-reviewer` before running. Confirm the effective policy
denies shell, delegation, other tools and every edit except the exact report path;
check external/read rules too. Inherited rules must not permit additional source
writes or unrelated external reads. Inspect any host-added tool-output exception
and ensure the outside-worktree `read` deny still applies to it. Managed configuration can take
precedence. If the installed version or merged policy cannot enforce this contract,
log the reason and skip this backend. The JSON above is v1 syntax; do not apply it
unchanged to v2. See [permissions](https://opencode.ai/docs/permissions/) and
[config precedence](https://opencode.ai/docs/config/).

Since shell execution is disabled, the caller materializes the exact resolved diff
to a temporary file first, with the same refs and pathspec. Give the reviewer both
the recorded command and that file's absolute path; tell it to read the saved diff
first, then inspect source with read/search tools. For plan review, it reads the plan
and source spec directly. Do not include implementation reasoning or prior findings.

```bash
OPENCODE_CONFIG_CONTENT="$(cat "$REVIEW_CONFIG")" opencode run --pure --agent inkstone-reviewer -m <provider/model> --title "review <SCOPE_LABEL>" "<prompt>" < /dev/null
```

- The prompt tells the reviewer to write the complete artifact to `REVIEW_FILE` using
  its file-writing tool and return a short completion message. It may not write any
  other path. A permission failure is a backend failure, not a reason to allow all edits.
- `--pure` disables external plugins; it does not remove project instructions,
  configuration or MCP servers. The dedicated policy limits tools; fresh context
  provides independence from the implementation conversation.
- `< /dev/null` for the same reason as Codex: never let a backgrounded reviewer wait on
  a stdin that no one will close.
- Redirect stdout to a file and watch that file; the same `tail`/`head` buffering trap
  applies (below).
- Smoke test the same agent and policy with a separate fresh report path: ask it to
  write `SMOKE OK` there, then check that file. A text-only smoke test does not verify
  the artifact permission. Generate the real run's config with its own report path.

Liveness: opencode has no rollout directory to probe. Use the run log — bytes written
should grow within the first minute; unchanged for 5 minutes is a hang; hard cap ~15
minutes. On failure, log it and fall through to backend 3.

---

## Backend 3 — context-blind subagents

Dispatch one subagent per lane with **Read/Glob/Grep only**, no shell, write tools
or delegation. Give it only the saved diff plus recorded command (or plan/spec),
its lane, and its report format. The host captures each reviewer's final message
verbatim into its designated lane report, like Codex's CLI output writer.
On Claude Code, use the plugin's `inkstone:inkstone-lane-reviewer` agent, defined in
`agents/inkstone-lane-reviewer.md` with `tools: Read, Glob, Grep`. Confirm that exact
restricted agent is available; do not silently dispatch `general-purpose` instead.
Other hosts must provide equivalent restricted execution **and** final-message
capture. If either is unavailable, this backend is unavailable. A file-scoped writer
is an alternative only when the host enforces the same source protection; never
grant unrestricted Write/Edit merely to save findings.
Do not include implementation reasoning or conversation history. Consolidate reports:
deduplicate (keep the most detailed duplicate), sort by severity.

Say plainly in the output and the artifact that the review was **same-model**, so its
independence is weaker.

---

## Watching any backend — two ways to blind yourself

A pass takes minutes to tens of minutes. Both of these make a healthy run look
identical to a wedged one, and both are easy to do by reflex.

**Never pipe it through `tail -N` or `head -N`.** They buffer to EOF, so the background
task's output file stays at **0 bytes for the whole run** however much the reviewer has
written.

```bash
# WRONG — nothing readable until the process exits
codex --sandbox read-only exec "$PROMPT" 2>&1 | tail -200
# RIGHT — write it all; filter when you READ the output file
# Run this whole supervisor block as ONE backgrounded tool invocation.
codex --sandbox read-only exec --output-last-message "$REVIEW_FILE" "$PROMPT" > "$OUT" 2>&1 < /dev/null &
REVIEW_PID=$!
printf '%s\n' "$REVIEW_PID" > "$PID_FILE"
if wait "$REVIEW_PID"; then REVIEW_EXIT=0; else REVIEW_EXIT=$?; fi
printf '%s\n' "$REVIEW_EXIT" > "$EXIT_FILE"
echo "reviewer exited (${REVIEW_EXIT}); output bytes: $(wc -c < "$OUT")"
```

The supervisor's shell stays alive until its child exits and records its status.
Use the same wrapper for OpenCode, replacing only the reviewer command. The host can
poll logs and run the backend's liveness/watchdog checks in separate tool calls;
those calls read saved PID/exit files, never inherit shell variables or try to
`wait` for another shell's child. For example, in a later tool call:

```bash
if [ -f "$EXIT_FILE" ]; then
  cat "$EXIT_FILE"
elif [ -f "$PID_FILE" ]; then
  REVIEW_PID=$(cat "$PID_FILE")
  ps -o etime=,time= -p "$REVIEW_PID"
fi
```

On timeout, read the current attempt's PID file and terminate that reviewer,
allowing the supervisor to record the exit. A missing exit file after the task has
ended is a supervisor failure, not success inferred from a report's existence.
Never use `pgrep -f` to identify or kill reviewers; it can match unrelated runs.
Apply the liveness and timeout checks while the supervisor runs.

`until [ ! -d /proc ]` is a real example of getting this wrong: macOS has no `/proc`, so
the loop body never executes and the watcher exits 0 having emitted nothing — which
reads exactly like "hasn't finished yet". Before arming any watcher, ask: **if the
reviewer died right now, what line would appear?** If the answer is "none", the watcher
is decorative.

Report elapsed time from a clock (`date`, `ps -o lstart=`), never from how many turns
have gone by.

**Don't wait idle.** Run the diff's own cheap checks alongside the pass — linters,
localization or script guards, a targeted test suite. On a 2026-09-10 sixlines-ios run
those found a real defect (Traditional orthography in a Simplified string) before Codex
returned anything at all.
