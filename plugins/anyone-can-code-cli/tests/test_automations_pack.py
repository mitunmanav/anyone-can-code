"""Improvement loop item 6: ready-made automation prompts users paste into Codex.

Doc-verified (app/automations.md): automations run scheduled prompts in the
background and report findings to the Triage inbox; pure prompt text, no deps.
"""

from __future__ import annotations

from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "automations" / "README.md"


def test_pack_exists_with_three_automations():
    text = PACK.read_text(encoding="utf-8")
    assert text.count("### ") >= 3, "need at least 3 ready-made automations"
    assert "Triage" in text  # tells user where results appear
    assert "archive" in text.lower()  # quiet when nothing to report


def test_prompts_carry_caveman_and_safety():
    text = PACK.read_text(encoding="utf-8")
    assert "caveman" in text.lower()
    assert "read-only" in text.lower() or "worktree" in text.lower()
