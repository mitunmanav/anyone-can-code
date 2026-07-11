"""Backlog 9: entry menu asked once + every session ends with a short recap.

Audit UX-9: real trial session ended with the user's question left hanging.
The menu is first_run.py (idempotent). The recap is a standing rule injected
at session start — the only doc-legal lever that shapes how a session ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(HOOKS))
sys.path.insert(0, str(SCRIPTS))

import load_session
import first_run


def test_session_context_contains_recap_rule(tmp_path):
    first_run.run_first_run(tmp_path, "builder")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "recap" in ctx.lower(), "session-end recap rule missing from context"
    assert "unanswered question" in ctx.lower()


def test_entry_menu_only_when_unconfigured(tmp_path):
    before = load_session.handle_payload({"source": "startup"}, tmp_path)
    ctx_before = before["hookSpecificOutput"]["additionalContext"]
    assert "FIRST RUN" in ctx_before

    first_run.run_first_run(tmp_path, "mixed")
    after = load_session.handle_payload({"source": "startup"}, tmp_path)
    ctx_after = after["hookSpecificOutput"]["additionalContext"]
    assert "FIRST RUN" not in ctx_after
