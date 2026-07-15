"""Style line in session context + count guidance in execute skill (B10, B12)."""
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "hooks" / "scripts"))
import load_session

STYLE_LINE = "Style: strict caveman. Short. Direct. No filler."
COUNT_LINE = "Do not hardcode test counts in docs."


class StyleContext(unittest.TestCase):
    def test_context_contains_style_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = load_session.build_context(Path(tmp), "startup")
            self.assertIn(STYLE_LINE, str(context))

    def test_execute_skill_has_count_rule(self):
        text = (PLUGIN_ROOT / "skills" / "execute" / "SKILL.md").read_text(
            encoding="utf-8")
        self.assertIn(COUNT_LINE, text)


if __name__ == "__main__":
    unittest.main()
