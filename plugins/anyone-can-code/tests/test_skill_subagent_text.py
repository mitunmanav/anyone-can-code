"""Backlog 8: orchestrator/plan skill text must EXPLICITLY instruct Codex to
spawn subagents (Codex only spawns when literally asked — doc-verified).

Each spawn instruction must carry: exact job, scope, expected output, and the
caveman style line.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def _read(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def test_orchestrator_has_explicit_spawn_template():
    text = _read("orchestrator")
    assert "Spawn a subagent" in text
    for token in ("Job:", "Scope:", "Expected output:"):
        assert token in text, f"orchestrator missing {token}"
    assert "caveman" in text.lower()


def test_plan_has_parallel_research_spawn_text():
    text = _read("plan")
    assert "Spawn a subagent" in text
    for token in ("Job:", "Scope:", "Expected output:"):
        assert token in text, f"plan missing {token}"


def test_spawn_text_keeps_control_with_acc():
    for name in ("orchestrator", "plan"):
        text = _read(name)
        assert "returns to ACC" in text or "return control to ACC" in text
