"""Tests for block-self-kill.py. Run: python3 hooks/test_block_self_kill.py"""
import json
from pathlib import Path
import subprocess
import unittest

HOOK = Path(__file__).with_name('block-self-kill.py')

CASES = {
    'pkill -f "next dev"': True,
    'pkill -9 -f next-server; echo done': True,
    'cd x && pgrep -af "node server"': True,
    'sudo pkill -f "vite"': True,
    'pkill --full vite': True,
    'pkill -f "[n]ext dev"': False,
    'pkill -f -u oasis "[v]ite"': False,
    'pkill node': False,
    'echo "pkill -f next dev"': False,
    'git commit -m "avoid pkill -f next"': False,
    'kill $(lsof -ti :3001)': False,
    'ls': False,
    'echo "unterminated': False,
}


def denied(command):
    out = subprocess.run(['python3', str(HOOK)], capture_output=True, text=True, check=True,
                         input=json.dumps({'tool_name': 'Bash', 'tool_input': {'command': command}}))
    if not out.stdout.strip():
        return False
    data = json.loads(out.stdout)
    return data['hookSpecificOutput']['permissionDecision'] == 'deny'


class BlockSelfKillTests(unittest.TestCase):
    def test_cases(self):
        for command, want in CASES.items():
            with self.subTest(command=command):
                self.assertEqual(denied(command), want)


if __name__ == '__main__':
    unittest.main()
