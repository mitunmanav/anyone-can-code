"""setup.py must not pollute user repo root with AGENTS.md (audit bug B5)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SETUP = PLUGIN_ROOT / "scripts" / "setup.py"


class SetupAgentsMd(unittest.TestCase):
    def run_setup(self, target, *extra):
        return subprocess.run(
            [sys.executable, str(SETUP), str(target), "--viewer", "none", *extra],
            capture_output=True, text=True, timeout=120)

    def test_default_skips_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_setup(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse((Path(tmp) / "AGENTS.md").exists())

    def test_write_flag_creates_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_setup(tmp, "--agents-md", "write")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(tmp) / "AGENTS.md").exists())

    def test_write_never_overwrites_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "AGENTS.md").write_text("user file\n", encoding="utf-8")
            self.run_setup(tmp, "--agents-md", "write")
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"),
                             "user file\n")


if __name__ == "__main__":
    unittest.main()
