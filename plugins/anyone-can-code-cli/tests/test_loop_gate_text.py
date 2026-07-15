"""Loop gate text exists in execute + orchestrator skills (B9)."""
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GATE = "After loop_budget iterations: STOP. Show real-use proof or ask user."


class LoopGate(unittest.TestCase):
    def test_gate_line_present(self):
        for name in ("execute", "orchestrator"):
            text = (PLUGIN_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(GATE, text, name)


if __name__ == "__main__":
    unittest.main()
