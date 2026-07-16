"""Sticky entry mode + task-aware scale (audit bugs B6, B13 / Idea 48)."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
import front_door


class StickyMode(unittest.TestCase):
    def test_second_call_reuses_stored_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = front_door.resolve_entry_mode(
                "improve my existing repo tests", root)
            second = front_door.resolve_entry_mode(
                "make it magical for everyone", root)
            self.assertEqual(second["entry_mode"], first["entry_mode"])
            self.assertEqual(second["entry_mode_source"], "stored")

    def test_reset_marker_reclassifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            front_door.resolve_entry_mode("improve my existing repo", root)
            fresh = front_door.resolve_entry_mode(
                "start over: brand new idea for a game", root)
            self.assertEqual(fresh["entry_mode_source"], "classified")


class TaskScale(unittest.TestCase):
    def test_scales(self):
        cases = {
            "fix typo in readme": "micro",
            "login button crashes on click": "bug",
            "add csv export feature": "feature",
            "research which db fits us": "research",
            "build me a waitlist site end to end": "product",
        }
        for request, want in cases.items():
            self.assertEqual(front_door.classify_task_scale(request), want, request)

    def test_loop_budget_in_contract(self):
        budget = front_door.loop_budget_for("micro")
        self.assertEqual(budget["iterations"], 1)


if __name__ == "__main__":
    unittest.main()
