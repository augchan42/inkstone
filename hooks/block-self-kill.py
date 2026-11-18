#!/usr/bin/env python3
"""PreToolUse hook (Bash): block `pkill -f` / `pgrep -f` patterns that match the tool's own shell.

The Bash tool runs each command as `bash -c "<command>"`. That shell's command line
contains the pattern, so `pkill -f "next dev"` kills the shell running it (exit 144)
and every later step in the same command is skipped. A bracket in the pattern
(`"[n]ext dev"`) still matches the target but not the literal text in the shell's argv.
"""
import json
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n", "|&"}
PREFIXES = {"sudo", "env", "nohup", "time", "command", "exec", "timeout", "nice"}


def commands(tokens):
    """Yield the token list of each simple command."""
    cur = []
    for tok in tokens:
        if tok in SEPARATORS:
            if cur:
                yield cur
            cur = []
        else:
            cur.append(tok)
    if cur:
        yield cur


def offending_pattern(cmd):
    # Skip leading wrappers (sudo, env VAR=1, timeout 5, ...).
    i = 0
    while i < len(cmd):
        t = cmd[i]
        if t in PREFIXES or "=" in t.split("/")[-1] and not t.startswith("-"):
            i += 1
        elif t.isdigit() and i > 0 and cmd[i - 1] == "timeout":
            i += 1
        else:
            break
    if i >= len(cmd):
        return None
    prog = cmd[i].split("/")[-1]
    if prog not in ("pkill", "pgrep"):
        return None
    args = cmd[i + 1:]
    full = False
    positional = []
    skip_next = False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a == "--full":
            full = True
        elif a.startswith("--"):
            if "=" not in a and a in ("--signal", "--uid", "--euid", "--group",
                                       "--parent", "--session", "--terminal",
                                       "--pidfile", "--ns", "--nslist", "--delimiter"):
                skip_next = True
        elif a.startswith("-") and len(a) > 1 and not a[1:].isdigit():
            flags = a[1:]
            if "f" in flags:
                full = True
            # Options that take a value as the next argument when given last.
            if flags[-1] in "gGPstuUFd":
                skip_next = True
        else:
            positional.append(a)
    if not full or not positional:
        return None
    pattern = positional[-1]
    if "[" in pattern:
        return None
    return pattern


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command") or ""
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lex.whitespace_split = True
        lex.whitespace = " \t\r"
        tokens = list(lex)
    except ValueError:
        return 0
    for cmd in commands(tokens):
        pattern = offending_pattern(cmd)
        if pattern is not None:
            fixed = "[" + pattern[0] + "]" + pattern[1:] if pattern else pattern
            reason = (
                f"Blocked: `-f {pattern!r}` matches this Bash tool call's own `bash -c` "
                "command line, so it would kill its own shell (exit 144) and skip the rest "
                f"of the command. Use the bracket trick (`-f \"{fixed}\"`), or kill by PID "
                "or port (e.g. `kill $(lsof -ti :3001)` or `fuser -k 3001/tcp`)."
            )
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }))
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
