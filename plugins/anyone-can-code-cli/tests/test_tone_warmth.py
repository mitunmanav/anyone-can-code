from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def test_narration_skills_are_warm_and_jargon_free():
    for skill in ("execute", "orchestrator", "clarify"):
        text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").lower()
        assert "plain words" in text, f"{skill}: missing plain-words rule"
        assert "no jargon" in text, f"{skill}: missing no-jargon rule"
        assert "not a robot" in text or "warm" in text, f"{skill}: missing warmth rule"


def test_skills_stay_within_budget():
    for skill in ("execute", "orchestrator", "clarify"):
        raw = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert len(raw) <= 4000, f"{skill}: over 4000 chars"
