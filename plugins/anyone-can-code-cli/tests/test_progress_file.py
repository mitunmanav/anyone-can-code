"""Improvement loop item 8: PROGRESS.md — the one file a non-coder can always open.

Rendered on every state write, plain words only.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import canonical_state


def _progress(tmp_path):
    return (tmp_path / ".codex" / "anyone-can-code" / "PROGRESS.md").read_text(encoding="utf-8")


def test_progress_rendered_on_every_state_write(tmp_path):
    canonical_state.update_canonical_state(
        tmp_path,
        {
            "active_goal": "waitlist website",
            "next_action": "add signup form",
            "next_steps": [
                {"step": "make the page", "status": "done"},
                {"step": "add signup form", "status": "pending"},
            ],
        },
    )
    text = _progress(tmp_path)
    assert "waitlist website" in text
    assert "add signup form" in text
    assert "[x] make the page" in text
    assert "What we are building" in text
    assert "What is next" in text


def test_progress_uses_plain_words_not_jargon(tmp_path):
    canonical_state.update_canonical_state(tmp_path, {"active_goal": "shop app"})
    text = _progress(tmp_path)
    for jargon in ("transaction_id", "schema_version", "capsule", "jsonl"):
        assert jargon not in text.lower(), f"jargon leaked: {jargon}"


def test_progress_shows_blocked_state(tmp_path):
    canonical_state.update_canonical_state(
        tmp_path, {"active_goal": "shop app", "failures": ["waiting on Stripe API key"]}
    )
    text = _progress(tmp_path)
    assert "needs you" in text.lower() or "waiting" in text.lower()
