"""Tests for rounds.py. Run: python3 -m unittest discover -s skills/codex-review/scripts"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rounds  # noqa: E402


def artifact(findings, reviewer="codex (gpt-6.1-sol)"):
    prose = "\n".join(f"### [{f.get('severity')}] {f.get('title')}" for f in findings)
    block = json.dumps({"findings": findings})
    return (f"---\nscope: x\nreviewer: \"{reviewer}\"\n---\n\n## Findings\n\n{prose}\n\n"
            f"## Verdict\n\nneeds revision\n\n```json\n{block}\n```\n")


def finding(fid, severity="high", cls="off-by-one", file="a.py", title=None):
    return {"id": fid, "severity": severity, "lane": "correctness", "class": cls,
            "file": file, "line": 3, "title": title or f"{cls} in {file} {fid}"}


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.old = os.getcwd()
        os.chdir(self.repo)
        for cmd in (["git", "init", "-q", "-b", "main"],
                    ["git", "config", "user.email", "t@example.com"],
                    ["git", "config", "user.name", "t"]):
            subprocess.run(cmd, check=True)
        self.base = self.commit("a.py", "x = 1\n")
        self.loop = Path("reviews/demo")
        self.loop.mkdir(parents=True)
        (self.loop / "decisions.md").write_text("No open questions. Scope: a.py.\n")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def commit(self, name, text):
        Path(name).write_text(text)
        subprocess.run(["git", "add", name], check=True)
        subprocess.run(["git", "commit", "-q", "-m", name], check=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()

    def run_cmd(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rounds.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def start(self, *extra):
        code, out, err = self.run_cmd("start", "demo", *extra)
        self.assertEqual(code, 0, err)
        return dict(line.split("=", 1) for line in out.splitlines())

    def review(self, n, findings):
        Path(self.loop / f"round-{n:02d}.md").write_text(artifact(findings))
        code, out, err = self.run_cmd("record", "demo", str(n))
        self.assertEqual(code, 0, err)
        return out

    def record(self, n):
        return json.loads((self.loop / f"round-{n:02d}.json").read_text())

    # ---------------------------------------------------------------- start

    def test_round_one_needs_decisions_and_base(self):
        (self.loop / "decisions.md").unlink()
        code, _, err = self.run_cmd("start", "demo", "--base", self.base)
        self.assertEqual(code, 2)
        self.assertIn("decisions.md", err)
        (self.loop / "decisions.md").write_text("Scope: a.py\n")
        code, _, err = self.run_cmd("start", "demo")
        self.assertIn("--base", err)

    def test_rejects_unsafe_ids_and_dirty_trees(self):
        code, _, err = self.run_cmd("start", "../x", "--base", self.base)
        self.assertEqual(code, 2)
        Path("a.py").write_text("dirty\n")
        code, _, err = self.run_cmd("start", "demo", "--base", self.base)
        self.assertEqual(code, 2)
        self.assertIn("committed snapshots", err)

    def test_files_in_the_loop_directory_do_not_count_as_dirty(self):
        head = self.commit("a.py", "x = 2\n")
        keys = self.start("--base", self.base)
        self.assertEqual(keys["DIFF_ARGS"], f"{self.base}..{head}")
        self.assertEqual(keys["ROUND"], "1")

    def test_round_two_reviews_only_the_increment_and_carries_context(self):
        h1 = self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1"), finding("F2", "low", "naming", title="bad name")])
        self.run_cmd("dispose", "demo", "1", "F2", "DECLINED", "--reason", "house style")
        h2 = self.commit("a.py", "x = 3\n")
        self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED", "--fixed-in", h2)
        keys = self.start()
        self.assertEqual(keys["DIFF_ARGS"], f"{h1}..{h2}")
        self.assertEqual(keys["FULL_DIFF_ARGS"], f"{self.base}..{h2}")
        ctx = Path(keys["CONTEXT"]).read_text()
        self.assertIn("bad name", ctx)
        self.assertIn("house style", ctx)
        self.assertIn("Repairs to verify", ctx)

    def test_next_round_refused_while_findings_are_undisposed(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1")])
        self.commit("a.py", "x = 3\n")
        code, _, err = self.run_cmd("start", "demo")
        self.assertEqual(code, 2)
        self.assertIn("1:F1", err)

    def test_empty_increment_and_rewritten_history_are_refused(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [])
        code, _, err = self.run_cmd("start", "demo")
        self.assertIn("nothing committed", err)
        subprocess.run(["git", "commit", "-q", "--amend", "-m", "rewritten"], check=True)
        code, _, err = self.run_cmd("start", "demo")
        self.assertIn("history rewritten", err)
        keys = self.start("--rebaseline")
        self.assertTrue(keys["DIFF_ARGS"].startswith(self.base))

    def test_an_incomplete_round_blocks_the_next(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.commit("a.py", "x = 3\n")
        code, _, err = self.run_cmd("start", "demo")
        self.assertIn("incomplete", err)

    # --------------------------------------------------------------- record

    def test_missing_or_malformed_json_is_incomplete_not_clean(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        md = self.loop / "round-01.md"
        md.write_text("## Findings\n\nnone\n")
        code, _, err = self.run_cmd("record", "demo", "1")
        self.assertEqual(code, 2)
        self.assertIn("incomplete, not clean", err)
        self.assertEqual(self.record(1)["status"], "started")
        for bad in ([{"id": "F1", "severity": "urgent"}],
                    [finding("F1"), finding("F1")],
                    [dict(finding("F1"), line=True)]):
            md.write_text(artifact(bad))
            code, _, _ = self.run_cmd("record", "demo", "1")
            self.assertEqual(code, 2)

    def test_prose_and_json_must_agree(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        text = artifact([finding("F1")]).replace("### [high]", "### [high] renamed")
        text = text.replace("off-by-one in a.py F1\n", "something else\n", 1)
        (self.loop / "round-01.md").write_text(text)
        code, _, err = self.run_cmd("record", "demo", "1")
        self.assertEqual(code, 2)
        self.assertIn("prose and JSON disagree", err)

    def test_recorded_findings_are_immutable_and_keep_the_reviewer(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1")])
        self.assertEqual(self.record(1)["reviewer"], "codex (gpt-6.1-sol)")
        code, _, err = self.run_cmd("record", "demo", "1")
        self.assertIn("immutable", err)

    def test_repeat_candidates_are_heuristic_until_confirmed(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1")])
        h = self.commit("a.py", "x = 3\n")
        self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED", "--fixed-in", h)
        self.start()
        out = self.review(2, [finding("G1")])
        self.assertIn("may repeat 1:F1 (class+file)", out)
        g1 = self.record(2)["findings"][0]
        self.assertEqual(g1["candidates"], [{"ref": "1:F1", "method": "class+file"}])
        self.run_cmd("dispose", "demo", "2", "G1", "ACCEPTED")
        self.assertEqual(self.record(2)["findings"][0]["disposition"]["origin"], "unknown")
        self.run_cmd("dispose", "demo", "2", "G1", "DECLINED", "--reason", "same as 1:F1",
                     "--duplicate-of", "1:F1")
        self.assertEqual(self.record(2)["findings"][0]["disposition"]["origin"], "re-raise")

    # -------------------------------------------------------------- dispose

    def test_dispose_rules(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1", "low")])
        code, _, err = self.run_cmd("dispose", "demo", "1", "F1", "DECLINED")
        self.assertIn("--reason", err)
        code, _, err = self.run_cmd("dispose", "demo", "1", "F1", "DEFERRED", "--reason", "x")
        self.assertIn("from round 4", err)
        code, _, err = self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED",
                                    "--fixed-in", "nope")
        self.assertEqual(code, 2)
        code, _, err = self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED",
                                    "--duplicate-of", "1:F1")
        self.assertIn("names no earlier finding", err)

    # -------------------------------------------------------------- verdict

    def test_verdict_follows_triage(self):
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1"), finding("F2", "medium", "docs", title="stale doc")])
        code, out, _ = self.run_cmd("verdict", "demo")
        self.assertEqual(code, 2)
        self.assertIn("INCOMPLETE", out)
        self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED")
        self.run_cmd("dispose", "demo", "1", "F2", "PRE-EXISTING", "--reason", "old")
        code, out, _ = self.run_cmd("verdict", "demo")
        self.assertEqual(code, 1)
        self.assertIn("no fix recorded", out)
        h = self.commit("a.py", "x = 3\n")
        self.run_cmd("dispose", "demo", "1", "F1", "ACCEPTED", "--fixed-in", h)
        code, out, _ = self.run_cmd("verdict", "demo")
        self.assertEqual(code, 1)
        self.assertIn("review their fixes", out)
        self.start()
        self.review(2, [finding("G1", "critical", "auth", "b.py", "unrelated")])
        self.run_cmd("dispose", "demo", "2", "G1", "PRE-EXISTING", "--reason", "on main")
        code, out, _ = self.run_cmd("verdict", "demo")
        self.assertEqual(code, 0)
        self.assertIn("VERDICT=STOP", out)
        self.assertIn("not approval to merge", out)

    def test_verdict_names_recurring_classes_and_deferred_items(self):
        last = self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        for n in range(1, 5):
            if n > 1:
                self.start()
            sev = "high" if n < 4 else "low"
            self.review(n, [finding(f"F{n}", sev, title=f"t{n}")])
            if n < 4:
                last = self.commit("a.py", f"x = {n + 10}\n")
                self.run_cmd("dispose", "demo", str(n), f"F{n}", "ACCEPTED",
                             "--fixed-in", last)
            else:
                self.run_cmd("dispose", "demo", "4", "F4", "DEFERRED", "--reason", "small")
        code, out, _ = self.run_cmd("verdict", "demo")
        self.assertEqual(code, 0)
        self.assertIn("deferred to one follow-up issue", out)
        self.assertIn("'off-by-one' recurred in rounds 1, 2, 3", out)

    # ---------------------------------------------------------------- stats

    def test_stats_reports_loops_and_ignores_one_shot_reviews(self):
        Path("reviews/review-20261023-x.md").write_text("one-shot\n")
        self.commit("a.py", "x = 2\n")
        self.start("--base", self.base)
        self.review(1, [finding("F1"), finding("F2", "low", "docs", title="doc")])
        code, out, _ = self.run_cmd("stats")
        self.assertEqual(code, 0)
        self.assertIn("| demo | 1 | 0 | 2 | 1 |", out)


if __name__ == "__main__":
    unittest.main()
