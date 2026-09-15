# Reviewer backends

Shared by `independent-review` (code) and `plan-review-loop` (plans). The skill decides
*what* to review and how to triage; this file decides *who* reviews it.

**The backend is incidental. The independence is the point.** A backend qualifies if it
has not seen the conversation that produced the change. Try them in this order and
**log which one actually ran and why the earlier ones were skipped** — a silent fallback
hides a fixable problem (on 2026-09-15 a Codex "quota failure" was a stdin deadlock).

| # | Backend | Independence | When it is skipped |
|---|---|---|---|
| 1 | Codex CLI (`codex exec`) | cross-model, cross-vendor | `codex` missing, quota exhausted, or dead after the liveness probe |
| 2 | opencode (`opencode run`) | cross-model; vendor depends on `-m` | `opencode` missing, or no model with quota |
| 3 | Context-blind subagents | **same model** — weaker; say so in the artifact | never — always available |

Record the result in the artifact frontmatter as tool **and** model, never the tool alone:

```
reviewer: codex-cli (gpt-5.x)
reviewer: opencode (opencode/muse-spark-1.3-contributor-free, agent plan) — codex: quota exhausted
reviewer: subagents (claude-fable-5-1, same-model) — codex: not installed; opencode: not installed
```

A free or small model is a legitimate backend, but a reader deciding how much to trust
the review needs to see which one it was.

---

## Backend 1 — Codex CLI

**Never use `codex exec review`.** That subcommand rejects a custom prompt, which makes
lanes and focus impossible. Always use plain `codex exec`.

Ensure multi-agent is enabled (idempotent):

```bash
CODEX_CONFIG="${HOME}/.codex/config.toml" && if [ ! -f "$CODEX_CONFIG" ]; then mkdir -p "${HOME}/.codex" && printf '[features]\nmulti_agent = true\n' > "$CODEX_CONFIG" && echo "Created ~/.codex/config.toml with multi_agent enabled"; elif ! grep -qE '^\s*multi_agent\s*=\s*true' "$CODEX_CONFIG"; then if grep -qE '^\[features\]' "$CODEX_CONFIG"; then if [ "$(uname)" = "Darwin" ]; then sed -i '' '/^\[features\]/a\'$'\n''multi_agent = true' "$CODEX_CONFIG"; else sed -i '/^\[features\]/a multi_agent = true' "$CODEX_CONFIG"; fi; else printf '\n[features]\nmulti_agent = true\n' >> "$CODEX_CONFIG"; fi && echo "Enabled multi_agent in ~/.codex/config.toml"; else echo "Codex multi-agent: already enabled"; fi
```

Run it **in the background** with a read-only sandbox — the reviewer reports findings,
it does not edit code:

```bash
codex --sandbox read-only exec "<prompt>" < /dev/null
```

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

```bash
opencode run --pure --agent plan -m <provider/model> --title "review <SCOPE_LABEL>" "<prompt>" < /dev/null
```

- `--agent plan` is opencode's built-in read-only agent. **The default agent is `build`,
  which can edit files** — a reviewer that edits is no longer a reviewer. If you ever run
  without `--agent plan`, confirm `git status` is unchanged afterwards and say so in the
  artifact.
- `--pure` keeps external plugins out of the run, so the prompt is the whole context.
- `< /dev/null` for the same reason as Codex: never let a backgrounded reviewer wait on
  a stdin that no one will close.
- Redirect stdout to a file and watch that file; the same `tail`/`head` buffering trap
  applies (below).
- Smoke test: `opencode run --pure --agent plan -m <model> "Reply with exactly: SMOKE OK" < /dev/null`.

Liveness: opencode has no rollout directory to probe. Use the run log — bytes written
should grow within the first minute; unchanged for 5 minutes is a hang; hard cap ~15
minutes. On failure, log it and fall through to backend 3.

---

## Backend 3 — context-blind subagents

Dispatch one subagent per lane, in parallel, each given **only** the diff (or plan)
command and its own lane. Do not tell them anything about the change's intent or your
reasoning — context-blindness is the entire point. Consolidate their findings yourself:
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
codex --sandbox read-only exec "$PROMPT" > "$OUT" 2>&1 < /dev/null
```

**Write the guard loop for the OS you are on.** Watch the process itself, not a proxy:

```bash
while pgrep -f "codex --sandbox read-only exec|opencode run" >/dev/null 2>&1; do sleep 20; done
echo "reviewer exited; output bytes: $(wc -c < "$OUT")"
```

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
