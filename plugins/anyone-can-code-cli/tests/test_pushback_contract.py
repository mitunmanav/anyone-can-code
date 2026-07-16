# plugins/anyone-can-code/tests/test_pushback_contract.py
"""Beta.4 T6: layered push-back - refuse plainly, or propose better and let user pick."""
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def test_pushback_layers_present_in_both_skills():
    for skill in ("clarify", "govern"):
        text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").lower()
        assert "impossible" in text, f"{skill}: layer 1 missing"
        assert "better way" in text, f"{skill}: layer 2 missing"
        assert "user picks" in text or "user decides" in text, f"{skill}: user choice missing"
