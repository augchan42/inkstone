# Review context for round 2

Approved decisions and scope for this change. Treat them as requirements.

# Decisions: codex-review loop mode

Approved in a design review with Codex (gpt-6.1-sol, high) on 2026-10-23.

- One-shot review stays the default and must behave exactly as before.
- Loop mode reviews committed snapshots only. Dirty tracked files are refused;
  untracked files are ignored. Rewritten history is refused unless `--rebaseline`.
- State is only the round records under `reviews/<id>/`. No hook, no background
  process. Committing them stays under Phase 6's existing rules.
- Origin of a finding is never inferred as "from-fix" by the script; it lists
  heuristic repeat candidates for the caller to confirm.
- The stop rule: stop when every finding is disposed, every ACCEPTED finding has a
  recorded fix commit, and the latest round accepted no critical/high finding.
  DECLINED and PRE-EXISTING findings never prolong the loop. STOP is not merge
  approval and there is no round cap.
- DEFERRED is allowed only for medium/low findings from round 4.
- Python 3 standard library only; Python is needed only for loop mode.

In scope to break: concurrent invocations on one loop, malformed or missing
reviewer output, unsafe loop ids and paths, history rewrites, pathspec drift,
running from a subdirectory of the repo, Windows (Git Bash) paths are best-effort.
Out of scope: authenticating who wrote a round record.

## Points already decided in earlier rounds

Do not raise these again unless the diff under review changes the reason given. Raising one again means saying what changed.

- none

## Repairs to verify

Earlier rounds accepted these. Check that the diff under review fixes them and does not break what they touch.

- [high] Output writes can follow symlinks outside the loop directory — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [high] Prose findings omitted from JSON silently disappear — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [medium] The documented path-limited start command fails argument parsing — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [medium] Changing working directories changes the loop scope — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [medium] Empty diffs are accepted as review rounds — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [medium] Round 100 is written but never loaded — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [low] Duplicate references accept nonexistent round zero — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
- [low] Confirmed repeats remain counted as unconfirmed candidates — `skills/codex-review/scripts/rounds.py` — fixed in c55a39d650190e599f1e6a373996781cd21be768
