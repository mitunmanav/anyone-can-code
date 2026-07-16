"""Improvement loop item 7: risky changes -> suggest Worktree mode in plain words.

Doc-verified (app/worktrees.md): Worktree = isolated second copy (Git only);
Handoff moves the thread back to Local when ready.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"

BUDGET = 4000


def test_execute_suggests_worktree_for_risky_work():
    text = (SKILLS / "execute" / "SKILL.md").read_text(encoding="utf-8")
    assert "Worktree" in text
    assert "safe copy" in text.lower()
    assert "git" in text.lower()  # honest limit: Git repos only
    assert "handoff" in text.lower()


def test_govern_uses_worktree_for_scope_jumps():
    text = (SKILLS / "govern" / "SKILL.md").read_text(encoding="utf-8")
    assert "Worktree" in text
    assert "safe copy" in text.lower()


def test_both_skills_stay_inside_budget():
    for name in ("execute", "govern"):
        size = len((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))
        assert size <= BUDGET, f"{name} over budget: {size}"
