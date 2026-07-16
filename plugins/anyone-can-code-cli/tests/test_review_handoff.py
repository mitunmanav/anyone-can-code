"""Improvement loop item 11: after code changes, point the user at the review pane.

Doc-verified (app/review.md): review pane shows diffs, inline comments,
stage/revert per file; Git repositories only.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def test_verify_hands_off_to_review_pane():
    text = (SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8")
    assert "review pane" in text.lower()
    assert "green" in text.lower() and "red" in text.lower()  # plain-words diff explain
    assert "revert" in text.lower()  # user can undo what they dislike


def test_verify_inside_budget_after_addition():
    size = len((SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"verify skill over budget: {size}"
