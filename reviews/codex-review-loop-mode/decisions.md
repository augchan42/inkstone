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
