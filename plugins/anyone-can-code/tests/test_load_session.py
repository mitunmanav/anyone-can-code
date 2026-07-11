"""Tests for load_session.build_context — UX-4 + GAP-6."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))

import load_session
import state


def test_load_context_includes_strong_comm_rule(tmp_path):
    """Context must say ENFORCE not just Talk:."""
    prefs_dir = tmp_path / ".codex" / "anyone-can-code" / "preferences"
    prefs_dir.mkdir(parents=True)
    (prefs_dir / "preferences.json").write_text(
        json.dumps({"communication_mode": "caveman-strict"}), encoding="utf-8"
    )
    ctx = load_session.build_context(tmp_path, "startup")
    assert "ENFORCE comm rule" in ctx


def test_load_context_includes_mistake_ledger(tmp_path):
    """Context must surface recent mistakes from mistake-ledger.jsonl."""
    state.ensure_project_layout(tmp_path)
    mistake_path = state.mistake_log_path(tmp_path)
    state.append_jsonl(mistake_path, {
        "timestamp": "2026-06-24T10:00:00Z",
        "signal_type": "style_correction",
        "detail": "Agent used too many words",
    })
    ctx = load_session.build_context(tmp_path, "startup")
    assert (
        "mistake" in ctx.lower()
        or "style_correction" in ctx.lower()
        or "Agent used too many words" in ctx
    )


def test_memory_notes_recalled_and_proof_written(tmp_path):
    """Backlog 3: lesson saved to memory/notes must come back next session, with proof."""
    import save_session
    save_session.durable_memory_writes(tmp_path, [
        {"signal_type": "manual_learn",
         "detail": "Always use real DB for deploys",
         "timestamp": "2026-07-06T10:00:00Z"},
    ], "session summary")

    ctx = load_session.build_context(tmp_path, "startup")
    assert "Always use real DB for deploys" in ctx, "saved lesson not recalled"

    workflow = state.read_state(tmp_path)
    assert workflow.get("memory_read_proof"), "memory_read_proof still empty"
