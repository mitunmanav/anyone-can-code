"""Handoff prompt builder (audit bug B8)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "build_handoff.py"
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))


class BuildHandoff(unittest.TestCase):
    def test_emits_all_required_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "--project-root", tmp],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            for needle in ("caveman", "Active goal", "Relevant memory",
                           "ACC orchestrator stays workflow owner"):
                self.assertIn(needle, r.stdout)


class GitStatusErrorHandling(unittest.TestCase):
    """Minor-5: subprocess.SubprocessError (e.g. TimeoutExpired) must not
    escape git_status -- only OSError was caught before, so a hung/killed
    git process crashed the whole handoff builder."""

    def test_timeout_expired_falls_back_gracefully(self):
        import build_handoff
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            subprocess, "run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=15),
        ):
            result = build_handoff.git_status(Path(tmp))
        self.assertEqual(result, "git unavailable")

    def test_called_process_error_falls_back_gracefully(self):
        import build_handoff
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            subprocess, "run",
            side_effect=subprocess.CalledProcessError(returncode=1, cmd="git"),
        ):
            result = build_handoff.git_status(Path(tmp))
        self.assertEqual(result, "git unavailable")


if __name__ == "__main__":
    unittest.main()
