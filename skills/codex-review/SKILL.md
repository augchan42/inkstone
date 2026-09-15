---
name: codex-review
description: Deprecated alias for independent-review, kept so "/inkstone:codex-review" and "codex review this" still work. The review is no longer tied to Codex — it runs on Codex CLI, opencode, or context-blind subagents, whichever is available. Use independent-review directly for new invocations.
user-invocable: true
argument-hint: "[scope] [paths] [--focus \"...\"] [--holistic] [--commit <sha>] [--pr <n>]"
metadata:
  version: "1.3.0"
  deprecated: true
---

# codex-review → independent-review

This name is kept for muscle memory only. The skill was renamed in v1.15.0 because the
value it delivers is a reviewer that has not seen your conversation, and Codex is just
one of three backends that provide that (Codex CLI, opencode, context-blind subagents).

**Do this and nothing else:** invoke the `independent-review` skill with exactly the
arguments you were given, then follow it. Do not run a review from this file.
