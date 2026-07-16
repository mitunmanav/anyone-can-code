"""Improvement loop item 4: verify must read the integrated terminal, not memory.

Doc-verified (app/features.md): Codex can read current terminal output to
check a running dev server or a failed build. Trial evidence: a timed-out
health check was claimed as success — never again.
"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def test_verify_requires_terminal_evidence():
    text = (SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8")
    assert "terminal" in text.lower()
    assert "read the terminal output" in text.lower()
    assert "never claim" in text.lower() or "never from memory" in text.lower()


def test_verify_stays_inside_token_budget():
    size = len((SKILLS / "verify" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"verify skill over budget: {size}"
