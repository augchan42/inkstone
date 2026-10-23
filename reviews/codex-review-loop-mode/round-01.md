---
scope: loop codex-review-loop-mode round 1: bfab61c5a4e8..2259932ba621
diff: git diff bfab61c5a4e8f46a57ff9b28c85811bae6cd6dde..2259932ba62127d3f83187a51d4726fd69f911c2
lanes: correctness, contracts, tests, security
reviewer: "codex (gpt-6.1-sol, high)"
---

## Findings

### [high] Output writes can follow symlinks outside the loop directory
**Where:** `skills/codex-review/scripts/rounds.py:102` · **Lane:** security

`write_atomic` writes through a predictable `.json.tmp` path without checking for symlinks. A pre-existing `reviews/demo/round-01.json.tmp` symlink to `../../README.md` makes `start` overwrite README before replacing the round record. The context write at line 206 similarly follows an existing symlink. Checking only the reviews and loop directories does not prevent these escapes. Create temporary files exclusively with unpredictable names, reject symlinked output destinations, and validate directory ancestors. Add symlink regression tests.

### [high] Prose findings omitted from JSON silently disappear
**Where:** `skills/codex-review/scripts/rounds.py:291` · **Lane:** correctness

Validation checks only that each JSON title appears somewhere in the prose. The reverse is unchecked: an artifact containing a high-severity finding followed by `{"findings": []}` is accepted as clean. This was reproduced with `parse_findings`; recording that output permits STOP without disposing the reported defect. Severity disagreements also pass. Require a one-to-one match between Markdown finding headings and JSON entries, including severity, and reject ambiguous multiple findings blocks. The existing disagreement test covers only the opposite direction.

### [medium] The documented path-limited start command fails argument parsing
**Where:** `skills/codex-review/scripts/rounds.py:502` · **Lane:** contracts

The documented command `start demo --base HEAD~1 -- src` exits 2 with `unrecognized arguments: -- src`. Combining the preceding positional argument, intervening options, and `paths` with `nargs="*"` prevents this ordering from parsing. Removing `--` still fails. Parse the path tail explicitly or otherwise support the documented argument order, and add a CLI regression test using that exact form.

### [medium] Changing working directories changes the loop scope
**Where:** `skills/codex-review/scripts/rounds.py:171` · **Lane:** correctness

Pathspecs are stored verbatim without their original working directory. A loop started at the repository root with `skills/codex-review` later emits the same pathspec when resumed from `skills/`, where Git interprets it as `skills/skills/codex-review`. Even supplying `--reviews-dir ../reviews` does not prevent this silent scope drift. The default reviews directory also follows the current directory instead of locating the existing repository loop. Anchor loop storage and pathspec interpretation to the repository root, preserving the meaning of paths supplied from subdirectories.

### [medium] Empty diffs are accepted as review rounds
**Where:** `skills/codex-review/scripts/rounds.py:188` · **Lane:** correctness

The only empty-increment check compares commit IDs. Different commits can have identical trees, or no changes within the fixed pathspec, so an empty commit, review-artifact-only commit, or unrelated commit can start an empty round. Round 1 also accepts `--base HEAD`. This contradicts the documented refusal of empty increments and allows a vacuous confirmation round. Check the actual scoped diff before creating records. The current test covers only unchanged HEAD.

### [medium] Round 100 is written but never loaded
**Where:** `skills/codex-review/scripts/rounds.py:86` · **Lane:** correctness

`round_path` produces `round-100.json`, but loading and statistics discover only two-digit filenames. After round 100 starts, `record ... 100` reports no such round, another start collides with the existing file, and verdict ignores the incomplete round. An in-memory loader probe with 100 records returned only 99. Discover arbitrary positive round numbers, sort numerically, and use the same discovery logic for statistics. This violates the explicit no-round-cap requirement.

### [low] Duplicate references accept nonexistent round zero
**Where:** `skills/codex-review/scripts/rounds.py:371` · **Lane:** correctness

The duplicate-reference check lacks a lower bound. `--duplicate-of 0:F1` indexes `rounds[-1]`, allowing a finding to reference itself in the latest round under a nonexistent round number. A read-only mocked invocation reproduced successful acceptance. Require `1 <= referenced_round < current_round` before indexing, and test zero explicitly.

### [low] Confirmed repeats remain counted as unconfirmed candidates
**Where:** `skills/codex-review/scripts/rounds.py:479` · **Lane:** contracts

Statistics count every finding with heuristic candidates even after its disposition confirms a repeat through `--duplicate-of`. A confirmed repeat therefore appears in both “confirmed repeats” and the documented unconfirmed-candidate count. A mocked statistics probe reproduced both counts as 1 for one confirmed finding. Exclude explicitly confirmed findings from the unconfirmed count and test statistics after duplicate disposition.

## Verification limitations

The requested unittest command was attempted. All 15 tests failed during setup because the read-only sandbox has no writable temporary directory; no test body ran.

Read-only probes confirmed argument parsing, omitted-prose acceptance, working-directory-dependent Git pathspec behavior, round-100 discovery, zero-round duplicate acceptance, and repeat statistics. Filesystem mutation and concurrency scenarios were inspected statically. No files were modified.

## Verdict

needs revision

```json
{"findings":[{"id":"F1","severity":"high","lane":"security","class":"symlink-write-escape","file":"skills/codex-review/scripts/rounds.py","line":102,"title":"Output writes can follow symlinks outside the loop directory"},{"id":"F2","severity":"high","lane":"correctness","class":"incomplete-findings-validation","file":"skills/codex-review/scripts/rounds.py","line":291,"title":"Prose findings omitted from JSON silently disappear"},{"id":"F3","severity":"medium","lane":"contracts","class":"argument-parsing","file":"skills/codex-review/scripts/rounds.py","line":502,"title":"The documented path-limited start command fails argument parsing"},{"id":"F4","severity":"medium","lane":"correctness","class":"working-directory-scope-drift","file":"skills/codex-review/scripts/rounds.py","line":171,"title":"Changing working directories changes the loop scope"},{"id":"F5","severity":"medium","lane":"correctness","class":"empty-diff-validation","file":"skills/codex-review/scripts/rounds.py","line":188,"title":"Empty diffs are accepted as review rounds"},{"id":"F6","severity":"medium","lane":"correctness","class":"round-number-discovery","file":"skills/codex-review/scripts/rounds.py","line":86,"title":"Round 100 is written but never loaded"},{"id":"F7","severity":"low","lane":"correctness","class":"duplicate-reference-bounds","file":"skills/codex-review/scripts/rounds.py","line":371,"title":"Duplicate references accept nonexistent round zero"},{"id":"F8","severity":"low","lane":"contracts","class":"repeat-statistics","file":"skills/codex-review/scripts/rounds.py","line":479,"title":"Confirmed repeats remain counted as unconfirmed candidates"}]}
```