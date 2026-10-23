---
scope: loop codex-review-loop-mode round 2: 2259932ba621..5dc8f62c54bd
diff: git diff 2259932ba62127d3f83187a51d4726fd69f911c2..5dc8f62c54bd5d4dbbe2ad992af6ee4be65e3dce
lanes: correctness, contracts, tests, security
reviewer: "codex (gpt-6.1-sol, high)"
---

## Findings

### [medium] Anchoring pathspecs changes their Git semantics
**Where:** `skills/codex-review/scripts/rounds.py:106` · **Lane:** correctness

Unconditionally prepending `:(top)` changes valid pathspecs. At the repository root, `-- .` becomes `:(top).`, which matches no files, causing `start` to refuse a nonempty change. Supplying `..` from an immediate subdirectory has the same result.

Existing magic is also lost: `:(glob)skills/**/*.py` becomes a literal unmatched pattern, while `:(exclude)skills/codex-review/scripts` stops excluding that directory. Read-only Git probes reproduced both failures against this increment. Preserve existing magic when anchoring the pattern, and encode repository-root scope correctly. Add regression tests for `.`, parent-directory scope, glob magic, and exclusions.

### [medium] Fenced examples are counted as finding headings
**Where:** `skills/codex-review/scripts/rounds.py:370` · **Lane:** correctness

The new comparison scans the entire Markdown text without respecting code fences. A valid finding containing a fenced Markdown example such as `### [low] Example heading` is rejected because that example is treated as an additional finding missing from JSON. This is particularly relevant when reviewing this repository’s Markdown skills and artifact examples.

An in-memory probe reproduced rejection of an artifact whose actual heading and JSON entry matched exactly. Extract actual headings within `## Findings`, ignoring fenced code, before comparing them with JSON. Add a regression test containing a fenced heading example.

## Verification limitations

The unit suite was attempted with bytecode writes disabled. All 23 tests failed during setup because the read-only sandbox has no writable temporary directory; no test body ran.

Read-only Git and in-memory parser probes reproduced the findings above. Filesystem writes, concurrent invocations, and the full CLI lifecycle were inspected statically. No files were modified.

## Verdict

needs revision

```json
{"findings":[{"id":"F1","severity":"medium","lane":"correctness","class":"pathspec-anchoring","file":"skills/codex-review/scripts/rounds.py","line":106,"title":"Anchoring pathspecs changes their Git semantics"},{"id":"F2","severity":"medium","lane":"correctness","class":"fenced-heading-validation","file":"skills/codex-review/scripts/rounds.py","line":370,"title":"Fenced examples are counted as finding headings"}]}
```