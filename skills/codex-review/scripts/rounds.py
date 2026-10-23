#!/usr/bin/env python3
"""codex-review loop mode: round records, dispositions, stop rule, statistics.

Loop mode is opt-in (`--loop <id>`). Each round is still one start-to-finish
invocation; this script only reads and writes the round records under
`<reviews-dir>/<id>/`, so later rounds can review the increment since the last
one and the caller can tell when to stop.

Usage:
    rounds.py start   <id> [--base REF] [--rebaseline] [--reviews-dir D] [-- PATH...]
    rounds.py record  <id> <round> [--reviews-dir D]
    rounds.py dispose <id> <round> <finding> <ACCEPTED|DECLINED|PRE-EXISTING|DEFERRED>
                      [--reason TEXT] [--fixed-in SHA] [--origin ORIGIN]
                      [--duplicate-of ROUND:FINDING] [--reviews-dir D]
    rounds.py verdict <id> [--reviews-dir D]
    rounds.py stats   [--reviews-dir D]

Files in <reviews-dir>/<id>/:
    decisions.md         written by the caller before round 1
    round-NN.md          the reviewer-written artifact
    round-NN.context.md  decisions and prior dispositions, given to the reviewer
    round-NN.json        the round record (this script owns it)

`start` prints KEY=value lines. `verdict` exits 0 to stop further rounds,
1 to continue, 2 when a round is incomplete or a finding has no disposition.
Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1
SEVERITIES = ("critical", "high", "medium", "low")
SERIOUS = ("critical", "high")
STATUSES = ("ACCEPTED", "DECLINED", "PRE-EXISTING", "DEFERRED")
ORIGINS = ("original", "from-fix", "re-raise", "new-scope", "unknown")
LOOP_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
FINDING_ID = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
JSON_BLOCK = re.compile(r"```json[ \t]*\n(.*?)\n```", re.S)
# Small findings from this round on are deferred to one follow-up issue.
DEFER_FROM_ROUND = 4


class Refusal(Exception):
    """A precondition failed; the message says what to do."""


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args: str) -> str:
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Refusal(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout.strip()


def loop_dir(reviews: Path, loop: str) -> Path:
    if not LOOP_ID.match(loop):
        raise Refusal(f"loop id {loop!r} must match {LOOP_ID.pattern}")
    if reviews.is_symlink():
        raise Refusal(f"{reviews} is a symlink; refusing")
    d = reviews / loop
    if d.is_symlink():
        raise Refusal(f"{d} is a symlink; refusing")
    return d


def round_path(d: Path, n: int, suffix: str) -> Path:
    return d / f"round-{n:02d}{suffix}"


def load_rounds(d: Path) -> list[dict]:
    rounds = []
    for p in sorted(d.glob("round-[0-9][0-9].json")):
        try:
            rec = json.loads(p.read_text())
        except ValueError as exc:
            raise Refusal(f"{p} is not valid JSON: {exc}") from exc
        if rec.get("schema") != SCHEMA:
            raise Refusal(f"{p} has schema {rec.get('schema')!r}, expected {SCHEMA}")
        rounds.append(rec)
    for i, rec in enumerate(rounds, start=1):
        if rec.get("round") != i:
            raise Refusal(f"{d}: round records are not numbered 1..{len(rounds)}")
    return rounds


def write_atomic(path: Path, rec: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


class Lock:
    """An exclusive lock file in the loop directory, for read-modify-write."""

    def __init__(self, d: Path, wait: float = 10.0):
        self.path, self.wait = d / ".lock", wait

    def __enter__(self):
        deadline = time.monotonic() + self.wait
        while True:
            try:
                os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                if time.monotonic() > deadline:
                    raise Refusal(f"{self.path} is held; another rounds.py is running, "
                                  "or remove it if none is") from None
                time.sleep(0.1)

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kv(**pairs) -> None:
    for k, v in pairs.items():
        print(f"{k}={v}")


# --------------------------------------------------------------------- start

def cmd_start(a) -> int:
    d = loop_dir(a.reviews_dir, a.loop)
    decisions = d / "decisions.md"
    if not decisions.is_file() or not decisions.read_text().strip():
        raise Refusal(
            f"write {decisions} first: each open question the spec leaves silent with "
            "its decision, and what is in scope to break. If there are none, say so "
            "and state the scope.")
    rel = os.path.relpath(d.resolve(), Path(git("rev-parse", "--show-toplevel")).resolve())
    # Untracked files are not part of a committed diff; modified tracked ones are.
    dirty = git("status", "--porcelain", "--untracked-files=no", "--", ":/",
                f":(top,exclude){rel}")
    if dirty:
        raise Refusal("loop mode reviews committed snapshots only; commit or stash:\n" + dirty)
    head = git("rev-parse", "HEAD")
    with Lock(d):
        rounds = load_rounds(d)
        if rounds and rounds[-1]["status"] != "reviewed":
            n = rounds[-1]["round"]
            raise Refusal(f"round {n} is incomplete: run `rounds.py record {a.loop} {n}` "
                          f"once {round_path(d, n, '.md')} is written, or delete "
                          f"{round_path(d, n, '.json')} to abandon it")
        undisposed = [f"{r['round']}:{f['id']}" for r in rounds for f in r["findings"]
                      if f.get("disposition") is None]
        if undisposed:
            raise Refusal("dispose every finding before the next round: "
                          + ", ".join(undisposed))
        n = len(rounds) + 1
        if n == 1:
            if not a.base:
                raise Refusal("round 1 needs --base REF (the commit the change starts from)")
            base = git("rev-parse", "--verify", a.base + "^{commit}")
            paths = list(a.paths)
            frm = base
        else:
            first, prev = rounds[0], rounds[-1]
            base, paths = first["base_sha"], first["pathspec"]
            if a.paths and list(a.paths) != paths:
                raise Refusal(f"the loop's pathspec is {paths}; it cannot change mid-loop")
            ancestor = subprocess.run(["git", "merge-base", "--is-ancestor",
                                       prev["head_sha"], head]).returncode == 0
            if a.rebaseline:
                frm = base
            elif not ancestor:
                raise Refusal(f"round {n - 1}'s head {prev['head_sha'][:12]} is not an "
                              "ancestor of HEAD (history rewritten). Re-run with "
                              "--rebaseline to review the whole change again.")
            else:
                frm = prev["head_sha"]
            if frm == head:
                raise Refusal("nothing committed since the last round; run "
                              f"`rounds.py verdict {a.loop}` instead")
        rec = {
            "schema": SCHEMA, "loop": a.loop, "round": n, "status": "started",
            "started_at": now(), "base_sha": base, "from_sha": frm, "head_sha": head,
            "rebaseline": bool(a.rebaseline and n > 1), "pathspec": paths,
            "diff_args": f"{frm}..{head}", "full_diff_args": f"{base}..{head}",
            "decisions_sha256": sha256(decisions), "reviewer": None, "findings": [],
        }
        jpath = round_path(d, n, ".json")
        try:
            fd = os.open(jpath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise Refusal(f"{jpath} already exists") from None
        os.close(fd)
        write_atomic(jpath, rec)
        ctx = round_path(d, n, ".context.md")
        ctx.write_text(context(rounds, decisions.read_text(), n))
    spec = " ".join(paths)
    kv(ROUND=n, ARTIFACT=round_path(d, n, ".md"), CONTEXT=ctx,
       DIFF_ARGS=rec["diff_args"], FULL_DIFF_ARGS=rec["full_diff_args"],
       PATHSPEC=spec, HEAD_SHA=head[:12],
       SCOPE_LABEL=f"loop {a.loop} round {n}: {frm[:12]}..{head[:12]}"
                   + (f" -- {spec}" if spec else "")
                   + (" (rebaseline: whole change)" if rec["rebaseline"] else ""))
    return 0


def context(rounds: list[dict], decisions: str, n: int) -> str:
    out = [f"# Review context for round {n}", "",
           "Approved decisions and scope for this change. Treat them as requirements.", "",
           decisions.strip(), ""]
    if n == 1:
        return "\n".join(out) + "\n"
    declined, repairs = [], []
    for r in rounds:
        for f in r["findings"]:
            disp = f["disposition"]
            where = f"`{f['file']}`" if f.get("file") else "(no file)"
            if disp["status"] in ("DECLINED", "PRE-EXISTING"):
                declined.append(f"- [{f['severity']}] {f['title']} — {where} — "
                                f"{disp['status']}: {disp['reason']}")
            elif disp["status"] == "ACCEPTED":
                repairs.append(f"- [{f['severity']}] {f['title']} — {where} — "
                               f"fixed in {disp.get('fixed_in') or '(no commit recorded)'}")
    out += ["## Points already decided in earlier rounds", "",
            "Do not raise these again unless the diff under review changes the reason "
            "given. Raising one again means saying what changed.", ""]
    out += declined or ["- none"]
    out += ["", "## Repairs to verify", "",
            "Earlier rounds accepted these. Check that the diff under review fixes them "
            "and does not break what they touch.", ""]
    out += repairs or ["- none"]
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------- record

def cmd_record(a) -> int:
    d = loop_dir(a.reviews_dir, a.loop)
    with Lock(d):
        rounds = load_rounds(d)
        if not 1 <= a.round <= len(rounds):
            raise Refusal(f"no round {a.round} in {d}")
        rec = rounds[a.round - 1]
        if rec["status"] == "reviewed":
            raise Refusal(f"round {a.round} is already recorded; findings are immutable")
        md = round_path(d, a.round, ".md")
        if not md.is_file():
            raise Refusal(f"{md} does not exist; the round has no artifact yet")
        text = md.read_text()
        findings = parse_findings(text)
        prior = [(r["round"], f) for r in rounds[: a.round - 1] for f in r["findings"]]
        for f in findings:
            f["candidates"] = candidates(f, prior)
            f["disposition"] = None
        rec.update(status="reviewed", reviewed_at=now(), reviewer=frontmatter(text, "reviewer"),
                   findings=findings)
        write_atomic(round_path(d, a.round, ".json"), rec)
    serious = sum(f["severity"] in SERIOUS for f in findings)
    print(f"round {a.round}: {len(findings)} findings, {serious} serious")
    for f in findings:
        for c in f["candidates"]:
            print(f"  {f['id']} may repeat {c['ref']} ({c['method']}); confirm with "
                  f"dispose --duplicate-of {c['ref']}")
    return 0


def parse_findings(text: str) -> list[dict]:
    blocks = JSON_BLOCK.findall(text)
    if not blocks:
        raise Refusal("the artifact has no ```json findings block; the round is "
                      "incomplete, not clean")
    raw = blocks[-1]
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        raise Refusal(f"the findings block is not valid JSON: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("findings"), list):
        raise Refusal('the findings block must be {"findings": [...]}')
    prose = text.replace(raw, "")
    seen, out = set(), []
    for i, f in enumerate(doc["findings"]):
        if not isinstance(f, dict):
            raise Refusal(f"finding {i} is not an object")
        fid = f.get("id")
        if not isinstance(fid, str) or not FINDING_ID.match(fid):
            raise Refusal(f"finding {i}: id {fid!r} must match {FINDING_ID.pattern}")
        if fid in seen:
            raise Refusal(f"duplicate finding id {fid}")
        seen.add(fid)
        if f.get("severity") not in SEVERITIES:
            raise Refusal(f"{fid}: severity must be one of {', '.join(SEVERITIES)}")
        for key in ("lane", "class", "title"):
            if not isinstance(f.get(key), str) or not f[key].strip():
                raise Refusal(f"{fid}: {key} must be a non-empty string")
        if f.get("file") is not None and not isinstance(f["file"], str):
            raise Refusal(f"{fid}: file must be a string or null")
        line = f.get("line")
        if line is not None and (not isinstance(line, int) or isinstance(line, bool)
                                 or line < 0):
            raise Refusal(f"{fid}: line must be a non-negative integer or null")
        if f["title"].strip() not in prose:
            raise Refusal(f"{fid}: title {f['title']!r} does not appear in the Markdown "
                          "findings; prose and JSON disagree")
        out.append({"id": fid, "severity": f["severity"], "lane": f["lane"],
                    "class": f["class"], "file": f.get("file"), "line": line,
                    "title": f["title"].strip()})
    return out


def frontmatter(text: str, key: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"') or None
    return None


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def candidates(f: dict, prior: list[tuple[int, dict]]) -> list[dict]:
    """Earlier findings this one may repeat. A heuristic for the caller to
    confirm, not a conclusion: two different bugs can share a class and file."""
    out = []
    for n, p in prior:
        if f["class"] == p["class"] and f.get("file") and f["file"] == p.get("file"):
            out.append({"ref": f"{n}:{p['id']}", "method": "class+file"})
            continue
        a, b = words(f["title"]), words(p["title"])
        if a and b and len(a & b) / len(a | b) >= 0.6:
            out.append({"ref": f"{n}:{p['id']}", "method": "title"})
    return out


# ------------------------------------------------------------------- dispose

def cmd_dispose(a) -> int:
    d = loop_dir(a.reviews_dir, a.loop)
    with Lock(d):
        rounds = load_rounds(d)
        if not 1 <= a.round <= len(rounds) or rounds[a.round - 1]["status"] != "reviewed":
            raise Refusal(f"round {a.round} is not a recorded round")
        rec = rounds[a.round - 1]
        f = next((x for x in rec["findings"] if x["id"] == a.finding), None)
        if f is None:
            raise Refusal(f"round {a.round} has no finding {a.finding}")
        if a.status != "ACCEPTED" and not a.reason:
            raise Refusal(f"{a.status} needs --reason")
        if a.status == "DEFERRED":
            if a.round < DEFER_FROM_ROUND or f["severity"] in SERIOUS:
                raise Refusal(f"only medium/low findings from round {DEFER_FROM_ROUND} on "
                              "can be DEFERRED to the follow-up issue")
        if a.fixed_in and a.status != "ACCEPTED":
            raise Refusal("--fixed-in applies to ACCEPTED findings only")
        fixed = git("rev-parse", "--verify", a.fixed_in + "^{commit}") if a.fixed_in else None
        if a.duplicate_of:
            m = re.match(r"^(\d+):(.+)$", a.duplicate_of)
            if not m or int(m.group(1)) >= a.round or not any(
                    x["id"] == m.group(2) for x in rounds[int(m.group(1)) - 1]["findings"]):
                raise Refusal(f"--duplicate-of {a.duplicate_of} names no earlier finding")
        origin = a.origin or ("original" if a.round == 1 else
                              "re-raise" if a.duplicate_of else "unknown")
        f["disposition"] = {"status": a.status, "reason": a.reason, "fixed_in": fixed,
                            "origin": origin, "duplicate_of": a.duplicate_of,
                            "at": now()}
        write_atomic(round_path(d, a.round, ".json"), rec)
    print(f"{a.round}:{a.finding} {a.status}" + (f" fixed in {fixed[:12]}" if fixed else ""))
    return 0


# ------------------------------------------------------------------- verdict

def cmd_verdict(a) -> int:
    d = loop_dir(a.reviews_dir, a.loop)
    rounds = load_rounds(d)
    if not rounds:
        raise Refusal(f"{d} has no rounds")
    last = rounds[-1]
    if last["status"] != "reviewed":
        kv(VERDICT="INCOMPLETE")
        print(f"round {last['round']} has no recorded findings; record or abandon it")
        return 2
    undisposed = [f"{r['round']}:{f['id']}" for r in rounds for f in r["findings"]
                  if f.get("disposition") is None]
    if undisposed:
        kv(VERDICT="INCOMPLETE")
        print("findings without a disposition: " + ", ".join(undisposed))
        return 2
    unfixed = [(r["round"], f) for r in rounds for f in r["findings"]
               if f["disposition"]["status"] == "ACCEPTED" and not f["disposition"]["fixed_in"]]
    serious_now = [f for f in last["findings"]
                   if f["severity"] in SERIOUS and f["disposition"]["status"] == "ACCEPTED"]
    deferred = [(r["round"], f) for r in rounds for f in r["findings"]
                if f["disposition"]["status"] == "DEFERRED"]
    if unfixed:
        kv(VERDICT="CONTINUE")
        print("accepted findings with no fix recorded (dispose --fixed-in SHA):")
        for n, f in unfixed:
            print(f"  {n}:{f['id']} [{f['severity']}] {f['title']}")
        code = 1
    elif serious_now:
        kv(VERDICT="CONTINUE")
        print(f"round {last['round']} accepted {len(serious_now)} serious finding(s); "
              "review their fixes in another round")
        code = 1
    else:
        kv(VERDICT="STOP")
        print(f"stop further review rounds: round {last['round']} accepted no serious "
              "finding and every accepted finding has a fix. This is a convergence rule, "
              "not approval to merge.")
        code = 0
    if deferred:
        print("deferred to one follow-up issue (file it under the project's own rules):")
        for n, f in deferred:
            print(f"  {n}:{f['id']} [{f['severity']}] {f['title']}")
    for line in repeats(rounds):
        print(line)
    hashes = {r["decisions_sha256"] for r in rounds}
    if len(hashes) > 1:
        print("decisions.md changed during the loop; declines made under an earlier "
              "version may no longer hold")
    return code


def repeats(rounds: list[dict]) -> list[str]:
    """Finding classes accepted, or confirmed as repeats, in two or more rounds."""
    seen: dict[str, set[int]] = {}
    for r in rounds:
        for f in r["findings"]:
            disp = f["disposition"]
            if disp["status"] == "ACCEPTED" or disp["duplicate_of"]:
                seen.setdefault(f["class"], set()).add(r["round"])
    return [f"class {c!r} recurred in rounds {', '.join(map(str, sorted(ns)))}: diagnose "
            "before fixing again — a decision missing from decisions.md, or a missing test"
            for c, ns in sorted(seen.items()) if len(ns) > 1]


# --------------------------------------------------------------------- stats

def cmd_stats(a) -> int:
    reviews = a.reviews_dir
    if not reviews.is_dir():
        raise Refusal(f"{reviews} is not a directory")
    print("| loop | rounds | incomplete | reported | serious | accepted | "
          "confirmed repeats | from-fix | heuristic repeat candidates | serious by round |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    any_loop = False
    for d in sorted(p for p in reviews.iterdir() if p.is_dir() and LOOP_ID.match(p.name)):
        if not list(d.glob("round-[0-9][0-9].json")):
            continue
        try:
            rounds = load_rounds(d)
        except Refusal as exc:
            print(f"| {d.name} | unreadable: {exc} |||||||||")
            continue
        any_loop = True
        done = [r for r in rounds if r["status"] == "reviewed"]
        fs = [f for r in done for f in r["findings"]]
        disp = [f["disposition"] for f in fs if f.get("disposition")]
        print("| " + " | ".join(map(str, [
            d.name, len(rounds), len(rounds) - len(done), len(fs),
            sum(f["severity"] in SERIOUS for f in fs),
            sum(x["status"] == "ACCEPTED" for x in disp),
            sum(x["origin"] == "re-raise" for x in disp),
            sum(x["origin"] == "from-fix" for x in disp),
            sum(bool(f.get("candidates")) for f in fs),
            ", ".join(str(sum(f["severity"] in SERIOUS for f in r["findings"])) for r in done),
        ])) + " |")
    if not any_loop:
        print("(no loop-mode reviews found)")
    print("\nCounts are of reported findings; accepted, repeats and from-fix count "
          "dispositions the caller confirmed. Heuristic candidates are unconfirmed.")
    return 0


# ---------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rounds.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--reviews-dir", type=Path, default=Path("reviews"))

    s = sub.add_parser("start")
    s.add_argument("loop")
    s.add_argument("--base")
    s.add_argument("--rebaseline", action="store_true")
    s.add_argument("paths", nargs="*")
    common(s)
    s = sub.add_parser("record")
    s.add_argument("loop")
    s.add_argument("round", type=int)
    common(s)
    s = sub.add_parser("dispose")
    s.add_argument("loop")
    s.add_argument("round", type=int)
    s.add_argument("finding")
    s.add_argument("status", choices=STATUSES)
    s.add_argument("--reason")
    s.add_argument("--fixed-in")
    s.add_argument("--origin", choices=ORIGINS)
    s.add_argument("--duplicate-of")
    common(s)
    s = sub.add_parser("verdict")
    s.add_argument("loop")
    common(s)
    s = sub.add_parser("stats")
    common(s)

    a = p.parse_args(argv)
    try:
        return {"start": cmd_start, "record": cmd_record, "dispose": cmd_dispose,
                "verdict": cmd_verdict, "stats": cmd_stats}[a.cmd](a)
    except Refusal as exc:
        print(f"rounds.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
