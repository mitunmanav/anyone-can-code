"""Tests for doctor.py CLI target argument (audit bug B2)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DOCTOR = PLUGIN_ROOT / "scripts" / "doctor.py"


class DoctorCliTarget(unittest.TestCase):
    def run_doctor(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(DOCTOR), *args],
            capture_output=True, text=True, timeout=60, cwd=cwd,
        )

    def test_accepts_positional_target_and_reports_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_doctor(str(tmp), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            evidence = json.dumps(payload)
            self.assertIn(Path(tmp).resolve().name, evidence)

    def test_missing_target_dir_exits_2(self):
        result = self.run_doctor(str(Path(tempfile.gettempdir()) / "no-such-dir-b2"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("not found", (result.stdout + result.stderr).lower())

    def test_file_as_target_exits_2_with_clear_stderr_error(self):
        """Minor-4: a file (not a directory) passed as project root must be
        rejected with a clear one-line stderr error and nonzero exit --
        not silently accepted because .exists() is True for files too."""
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "not-a-directory.txt"
            file_path.write_text("hello", encoding="utf-8")
            result = self.run_doctor(str(file_path))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("not a directory", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
