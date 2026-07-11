"""Improvement loop item 12: orchestrator suggests Cloud mode for long tasks.

Doc-verified (app/features.md modes + cloud/overview.md): Cloud threads run
remotely in the background; Local/Worktree run on the computer; Cloud needs
GitHub connected.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def test_orchestrator_suggests_cloud_for_long_tasks():
    text = (SKILLS / "orchestrator" / "SKILL.md").read_text(encoding="utf-8")
    low = text.lower()
    assert "cloud" in low
    assert "long" in low or "big" in low  # trigger: long/big tasks
    assert "sleep" in low or "background" in low  # plain-words benefit
    assert "github" in low  # known requirement, honest limit


def test_orchestrator_inside_budget_after_addition():
    size = len((SKILLS / "orchestrator" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"orchestrator skill over budget: {size}"
