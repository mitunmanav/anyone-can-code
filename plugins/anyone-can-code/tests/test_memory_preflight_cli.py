"""Tests for memory_preflight CLI ergonomics (audit bug B3)."""
import subprocess
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "memory_preflight.py"


class PreflightCli(unittest.TestCase):
    def test_help_shows_worked_example(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertIn("Example:", r.stdout)
        self.assertIn("--project-root", r.stdout)

    def test_blank_request_exits_2_with_hint(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "   "],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("request text required", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
