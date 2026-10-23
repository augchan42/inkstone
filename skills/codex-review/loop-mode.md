# Loop mode

Opt-in with `--loop <id>`. Use it when a change will be reviewed more than once.
One-shot review stays the default and is unchanged.

**Why it exists.** In one project's 256 review loops, rounds were unbounded and each
round sent the whole branch to a fresh reviewer with no record of what had been
decided. Loops ran up to 52 rounds. From round 6 on, 38% of findings were defects
introduced by the previous round's fix, 21% re-raised points already declined, and 4%
of code-loop findings were serious. Loops ended within one to three rounds once the
open requirements question was written down. Loop mode makes those lessons
mechanical: decide first, review the increment, record findings as data, stop by rule.

**What it is not.** It is not a background loop or a hook. Each round is one
invocation that runs start to finish. Its state is the round records under
`reviews/<id>/`, which the caller reads and may commit (Phase 6 still decides that).
The verdict says when to stop *reviewing*; it is never approval to merge.

`rounds.py` is `scripts/rounds.py` in this skill's installed directory. Run it from
the target repository, with Python 3 (standard library only). One-shot reviews do not
need Python.

## Before round 1: `reviews/<id>/decisions.md`

Write it before the first round; `rounds.py start` refuses without it. It holds:

- each question the spec or issue leaves open that the change has to answer, with the
  decision taken (or "unresolved — blocks review of X", honestly);
- what is in scope to break: a short threat model, or the inputs and failures the
  change must handle and the ones it need not;
- if nothing is open, say "No open questions" and state the scope.

Approved requirements and constraints only. Not implementation reasoning: the
reviewer still must not see why the author believes the code is right.

Its SHA-256 is stored with every round. If it changes mid-loop, the verdict says so,
because declines made under the earlier version may no longer hold.

## Each round

Loop mode reviews committed snapshots only. Commit first; untracked files are ignored,
modified tracked files are refused.

1. **Start** — instead of `resolve-scope.sh`:

   ```bash
   python3 "<skill dir>/scripts/rounds.py" start <id> --base <ref> [-- <paths>]   # round 1
   python3 "<skill dir>/scripts/rounds.py" start <id>                             # later rounds
   ```

   It prints `ROUND`, `ARTIFACT`, `CONTEXT`, `DIFF_ARGS`, `FULL_DIFF_ARGS`,
   `PATHSPEC`, `HEAD_SHA`, `SCOPE_LABEL`. Echo `SCOPE_LABEL` as in Phase 1.
   Round 1's diff is `<base>..HEAD`. Round N's is the previous round's head to HEAD.
   It refuses: a dirty tree, an unsafe id, an incomplete earlier round, undisposed
   findings, an empty diff (in round 1 too, after the pathspec), and rewritten history (`--rebaseline` reviews the
   whole change again). The pathspec is fixed by round 1 and stored relative to the repository root;
   `reviews/` defaults to the repository root too, so any subdirectory gives the same loop.

2. **Review** — Phases 2 and 3 as usual, with these differences in the prompt:
   - the diff command is `git diff <DIFF_ARGS> [-- <PATHSPEC>]`; review it first;
   - give `git diff <FULL_DIFF_ARGS>` as context only: findings must be in the
     increment or caused by it, including its effects elsewhere in the code;
   - include the `CONTEXT` file verbatim. It holds `decisions.md`, every earlier
     DECLINED or PRE-EXISTING finding with its reason (not to be re-raised unless the
     increment changes the reason), and every ACCEPTED finding's claimed repair, to
     verify. For OpenCode this is the one permitted exception to "no prior findings";
   - the reviewer writes the artifact to `ARTIFACT` (not the one-shot
     `reviews/review-<ts>-<sha>.md` path), with the Phase 4 Markdown, and ends its own
     part with one fenced JSON block:

     ````markdown
     ```json
     {"findings": [{"id": "F1", "severity": "high", "lane": "correctness",
                    "class": "off-by-one", "file": "src/a.py", "line": 42,
                    "title": "<the same title as its ### heading>"}]}
     ```
     ````

     `severity` is critical, high, medium or low; `class` is a short kebab-case slug
     for the kind of defect; `id`s are unique in the round; `file`/`line` may be null.
     With lane subagents, the consolidating step assigns ids and writes the one block.
     No findings is `{"findings": []}`, never a missing block.

3. **Record** — `rounds.py record <id> <N>`. It validates the block (one block only; types,
   enums, unique ids; each `### [severity] title` heading under the findings matches one
   JSON entry, severity included) and stores the findings. A missing or
   malformed block leaves the round incomplete: it never counts as clean. Recorded
   findings are immutable. It lists *possible* repeats of earlier findings (same
   class and file, or similar title) for you to confirm or reject.

4. **Triage** — Phase 5's judgement, recorded per finding:

   ```bash
   rounds.py dispose <id> <N> <finding> ACCEPTED [--fixed-in <sha>]
   rounds.py dispose <id> <N> <finding> DECLINED --reason "..." [--duplicate-of 1:F3]
   rounds.py dispose <id> <N> <finding> PRE-EXISTING --reason "..."
   rounds.py dispose <id> <N> <finding> DEFERRED --reason "..."   # round 4+, medium/low
   ```

   `--origin original|from-fix|re-raise|new-scope|unknown` records where a finding came
   from, when you know. Default: `original` in round 1, `re-raise` with
   `--duplicate-of`, otherwise `unknown`. Do not guess `from-fix`; the statistics
   are only as good as these.

5. **Fix** accepted findings (Phase 6 rules apply), commit, then
   `dispose ... ACCEPTED --fixed-in <sha>`.

6. **Verdict** — `rounds.py verdict <id>`:
   - `INCOMPLETE` (exit 2): a round has no recorded findings, or a finding has no
     disposition;
   - `CONTINUE` (exit 1): an accepted finding has no fix recorded, or the latest
     round accepted a serious (critical/high) finding, whose fix needs a round;
   - `STOP` (exit 0): stop further review rounds.

   Declined and pre-existing findings never prolong the loop. DEFERRED findings are
   listed for one follow-up issue, filed under the project's own rules. A class
   accepted (or confirmed as a repeat) in two or more rounds is named: stop and
   diagnose before fixing it again — usually a decision missing from
   `decisions.md`, sometimes a missing test. Serious findings can keep a loop going;
   this is a convergence rule, not a round cap.

## Statistics

`rounds.py stats [--reviews-dir reviews]` prints one row per loop: rounds, incomplete
rounds, reported and serious findings, accepted, confirmed repeats and from-fix
counts (from your dispositions), unconfirmed repeat candidates, and serious findings
by round. One-shot artifacts are ignored. The counts describe reported findings and
your dispositions; they do not establish what caused a finding.
