"""CLI wrappers for state scripts (audit bug B4)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CANON = PLUGIN_ROOT / "scripts" / "canonical_state.py"
COORD = PLUGIN_ROOT / "scripts" / "task_coordination.py"


class StateCli(unittest.TestCase):
    def test_show_prints_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(CANON), "show", "--repo-root", tmp],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertIn("active_goal", data)

    def test_update_sets_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(CANON), "update", "--repo-root", tmp,
                 "--set", "active_goal=ship the CLI"],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run(
                [sys.executable, str(CANON), "show", "--repo-root", tmp],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(json.loads(r.stdout)["active_goal"], "ship the CLI")

    def test_update_rejects_unknown_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(CANON), "update", "--repo-root", tmp,
                 "--set", "not_a_real_key=1"],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, "", "Minor-6: error text must not go to stdout")
            self.assertIn("unknown key", r.stderr.lower())

    def test_coordination_status_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(COORD), "status", "--repo-root", tmp],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_coordination_claim_error_goes_to_stderr(self):
        """Minor-6: task_coordination.py CLI error paths must print to
        stderr, not stdout; exit code stays 2."""
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(COORD), "claim", "--repo-root", tmp,
                 "--task-id", "does-not-exist"],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, "", "Minor-6: error text must not go to stdout")
            self.assertIn("not found", r.stderr.lower())


if __name__ == "__main__":
    unittest.main()
