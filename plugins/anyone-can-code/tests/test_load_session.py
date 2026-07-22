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


def test_recall_reads_scoped_note_folders(tmp_path):
    notes = tmp_path / ".codex" / "anyone-can-code" / "memory" / "notes" / "project"
    notes.mkdir(parents=True)
    notes.joinpath("lesson-1.md").write_text(
        "---\nkind: \"lesson\"\nstatus: \"active\"\nreinforcement_count: 3\n---\n"
        "# Lesson\n\n## Summary\n\nAlways run npm.cmd on Windows\n",
        encoding="utf-8",
    )
    lessons, proof = load_session.recall_memory_notes(tmp_path)
    assert any("npm.cmd" in line for line in lessons)
    assert proof


def test_recall_skips_revoked_and_caps_size(tmp_path):
    notes = tmp_path / ".codex" / "anyone-can-code" / "memory" / "notes" / "project"
    notes.mkdir(parents=True)
    notes.joinpath("revoked.md").write_text(
        "---\nkind: \"lesson\"\nstatus: \"revoked\"\n---\n\n## Summary\n\nOld wrong lesson\n",
        encoding="utf-8",
    )
    for i in range(50):
        notes.joinpath(f"l{i}.md").write_text(
            f"---\nkind: \"lesson\"\nstatus: \"active\"\nreinforcement_count: {i}\n---\n"
            f"\n## Summary\n\nLesson number {i} with a reasonably long sentence attached\n",
            encoding="utf-8",
        )
    lessons, _ = load_session.recall_memory_notes(tmp_path)
    joined = "\n".join(lessons)
    assert "Old wrong lesson" not in joined
    assert len(joined) <= 1200


def test_session_context_includes_loops_and_plugin_root(tmp_path):
    """SessionStart must call loop_registry for real and inject ACC_PLUGIN_ROOT."""
    out = load_session.build_context(tmp_path, "startup")
    assert "ACC_PLUGIN_ROOT=" in out
    assert "Loops:" in out
    assert "work=on" in out
    assert "scheduled=opt-in" in out
    assert "self_improve=opt-in" in out

def test_load_lean_skips_tier_c_loops(tmp_path, monkeypatch):
    """ACC_LOAD_LEAN=1 keeps Tier A (ENFORCE) but skips loop parade."""
    monkeypatch.setenv("ACC_LOAD_LEAN", "1")
    prefs = tmp_path / ".codex" / "anyone-can-code" / "settings"
    prefs.mkdir(parents=True)
    (prefs / "preferences.json").write_text(
        __import__("json").dumps({"communication_mode": "caveman-strict"}),
        encoding="utf-8",
    )
    ctx = load_session.build_context(tmp_path, "startup")
    assert "ENFORCE comm rule" in ctx
    assert "ACC_PLUGIN_ROOT=" in ctx
    assert "Loops:" not in ctx

