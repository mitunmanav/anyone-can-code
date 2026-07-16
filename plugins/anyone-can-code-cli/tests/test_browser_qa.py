"""Improvement loop item 5: web products get eyes-on QA via the in-app browser.

Doc-verified (app/browser.md): Codex can operate the in-app browser with
@Browser (click, type, screenshot, inspect rendered state) for local dev
servers; no signed-in pages.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def test_verify_has_browser_qa_instruction():
    text = (SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8")
    assert "@Browser" in text
    assert "in-app browser" in text.lower()
    assert "unverified" in text.lower()  # honest fallback when browser unavailable
    assert "login" in text.lower() or "signed-in" in text.lower()  # known limit


def test_verify_still_inside_token_budget():
    size = len((SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"verify skill over budget: {size}"
