import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HOOK = Path(sys.argv.pop(1)).resolve() if len(sys.argv) > 1 else Path(__file__).with_name('stop-hook.sh')
REVIEW_ID = '20261027-100000-abcdef'


class StopHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.claude').mkdir()
        (self.root / 'reviews').mkdir()
        self.state = self.root / '.claude/plan-review-loop.local.md'
        self.review = self.root / f'reviews/plan-review-{REVIEW_ID}.md'

    def activate(self, phase='review', **fields):
        data = dict(active='true', phase=phase, review_id=REVIEW_ID)
        data.update(fields)
        self.state.write_text(''.join(f'{k}: {v}\n' for k, v in data.items()))

    def run_hook(self, expected='allow', continued=False, env=None):
        result = subprocess.run(['bash', str(HOOK)], cwd=self.root,
                                input=json.dumps({'stop_hook_active': continued}),
                                text=True, capture_output=True, timeout=5, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertIsInstance(output, dict)
        # Stop accepts an omitted decision or "block"; "approve" is invalid.
        self.assertIn(output.get('decision'), (None, 'block'), output)
        if expected == 'block':
            self.assertEqual(output.get('decision'), 'block')
            self.assertTrue(output.get('reason'))
        else:
            self.assertNotIn('decision', output)
        return output

    def test_no_state(self):
        self.run_hook()

    def test_defer_to_original(self):
        self.activate()
        (self.root / '.claude/review-loop.local.md').touch()
        self.run_hook()
        self.assertTrue(self.state.exists())

    def test_locate_and_review_block(self):
        for phase in ('locate', 'review'):
            with self.subTest(phase=phase):
                self.activate(phase)
                self.run_hook('block')
                self.assertIn('hook_blocks: 1', self.state.read_text())

    def test_block_budget_fails_open(self):
        self.activate()
        self.run_hook('block')
        self.run_hook('block', continued=True)
        self.run_hook(continued=True)
        self.assertFalse(self.state.exists())

    def test_addressing_blocks_without_disposition(self):
        self.activate('addressing')
        self.review.write_text('# Findings\n')
        self.run_hook('block')

    def test_addressing_allows_after_disposition(self):
        self.activate('addressing')
        self.review.write_text('## Disposition\nFIXED\n')
        self.run_hook()
        self.assertFalse(self.state.exists())

    def test_missing_review_fails_open(self):
        for phase in ('addressing', 'confirm'):
            with self.subTest(phase=phase):
                self.activate(phase)
                self.run_hook()
                self.assertFalse(self.state.exists())

    def test_confirm_blocks_without_verdict(self):
        self.activate('confirm')
        self.review.write_text('## Disposition\nFIXED\n')
        self.run_hook('block')

    def test_confirm_allows_after_verdict(self):
        self.activate('confirm')
        self.review.write_text('## Confirmation\nResolved\n')
        self.run_hook()
        self.assertFalse(self.state.exists())

    def test_invalid_id_inactive_and_unknown_phase(self):
        for fields in ({'review_id': '../../escape'}, {'active': 'false'}, {'phase': 'unknown'}):
            with self.subTest(fields=fields):
                self.activate(**fields)
                self.run_hook()
                self.assertFalse(self.state.exists())

    def test_error_trap_fails_open(self):
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        cat = bin_dir / 'cat'
        cat.write_text('#!/bin/sh\nexit 1\n')
        cat.chmod(0o755)
        self.run_hook(env={**os.environ, 'PATH': f'{bin_dir}:{os.environ["PATH"]}'})


if __name__ == '__main__':
    unittest.main()
