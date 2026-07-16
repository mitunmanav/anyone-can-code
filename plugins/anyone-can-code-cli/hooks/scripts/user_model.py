"""Tiny user model. An "about you" block in preferences.json that grows ONLY
from explicit user corrections — never from guesses. Injected at session
start as one capped line."""

from __future__ import annotations

from pathlib import Path

import state

ALLOWED_FIELDS = {"skill_level", "reply_taste", "stack"}
VALUE_MAX = 80
LINE_MAX = 240


def record_correction(repo_root: Path, field: str, value: str) -> bool:
    """Save one explicit correction. Unknown fields are ignored on purpose."""
    if field not in ALLOWED_FIELDS or not str(value).strip():
        return False
    prefs = state.read_preferences(repo_root)
    about = dict(prefs.get("about_you") or {})
    about[field] = str(value).strip()[:VALUE_MAX]
    state.write_preferences(repo_root, {"about_you": about})
    return True


def about_you_line(repo_root: Path) -> str:
    """One capped line for session-start injection; empty when nothing saved."""
    about = state.read_preferences(repo_root).get("about_you") or {}
    parts = [f"{field}={about[field]}" for field in sorted(ALLOWED_FIELDS) if about.get(field)]
    if not parts:
        return ""
    return f"About you (from your corrections): {'; '.join(parts)}."[:LINE_MAX]
