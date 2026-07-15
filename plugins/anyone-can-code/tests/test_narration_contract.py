# plugins/anyone-can-code/tests/test_narration_contract.py
"""Beta.4 T5: build steps narrated in plain words, no code shown."""
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def read(skill: str) -> str:
    return (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").lower()


def test_execute_carries_narration_contract():
    text = read("execute")
    assert "narrate" in text
    assert "no code shown" in text
    assert "done" in text


def test_orchestrator_carries_narration_contract():
    text = read("orchestrator")
    assert "narrate" in text


def test_both_fit_budget():
    for skill in ("execute", "orchestrator"):
        raw = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert len(raw) <= 4000
