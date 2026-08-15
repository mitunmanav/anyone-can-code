"""Raw capture format + script mine rules (park-raw-mine v1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(HOOKS))
sys.path.insert(0, str(SCRIPTS))

import guard
import raw_capture
import raw_mine
import save_session
import state


def test_build_raw_entry_user_role_and_fields():
    entry = raw_capture.build_raw_entry(
        role="user",
        text="please always use blue buttons",
        payload={"session_id": "s1", "turn_id": "t1"},
        source=raw_capture.SOURCE_USER,
    )
    assert entry is not None
    assert entry["role"] == "user"
    assert entry["text"] == "please always use blue buttons"
    assert entry["schema_version"] == 1
    assert entry["session_id"] == "s1"
    assert entry["turn_id"] == "t1"
    assert entry["source"] == "hook:UserPromptSubmit"
    assert entry["content_hash"]
    assert entry["secret_redacted"] is False


def test_build_raw_entry_redacts_secrets():
    # Fake token for unit test — pattern matches memory_core.scrub
    dirty = "deploy with api_key: sk-abcdefghijklmnop99 now"
    entry = raw_capture.build_raw_entry(role="user", text=dirty, payload={})
    assert entry is not None
    assert "sk-abcdefghijklmnop99" not in entry["text"]
    assert "[REDACTED]" in entry["text"]
    assert entry["secret_redacted"] is True


def test_capture_user_and_assistant_separate_roles(tmp_path):
    raw_capture.capture_user_prompt(
        tmp_path,
        {
            "prompt": "I prefer short caveman answers",
            "session_id": "sess-a",
            "turn_id": "turn-1",
        },
    )
    raw_capture.capture_assistant_turn(
        tmp_path,
        {
            "last_assistant_message": "OK. Next: wire the form.",
            "session_id": "sess-a",
            "turn_id": "turn-1",
        },
    )
    turns = raw_capture.read_raw_turns(tmp_path)
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[1]["role"] == "assistant"
    assert "caveman" in turns[0]["text"]
    assert "wire the form" in turns[1]["text"]
    path = raw_capture.raw_turns_path(tmp_path)
    assert path.name == "turns.jsonl"
    assert "memory" in path.parts and "raw" in path.parts


def test_guard_user_prompt_writes_raw(tmp_path):
    out = guard.handle_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "always use real DB for deploys",
            "session_id": "s",
            "turn_id": "t",
        },
        tmp_path,
    )
    assert "hookSpecificOutput" in out
    turns = raw_capture.read_raw_turns(tmp_path)
    assert len(turns) >= 1
    assert turns[-1]["role"] == "user"
    assert "real DB" in turns[-1]["text"]


def test_save_session_writes_assistant_raw(tmp_path):
    payload = {
        "hook_event_name": "Stop",
        "last_assistant_message": "We decided to go with SQLite for storage.",
        "turn_id": "t-stop",
        "session_id": "s-stop",
    }
    save_session.handle_payload(payload, tmp_path)
    turns = raw_capture.read_raw_turns(tmp_path)
    assert any(t["role"] == "assistant" and "SQLite" in t["text"] for t in turns)


def test_mine_rule_preference_from_user_raw(tmp_path):
    raw_capture.capture_user_prompt(
        tmp_path,
        {
            "prompt": "From now on please always use the blue theme on every page.",
            "turn_id": "t1",
        },
    )
    # assistant noise should not mine as preference primary path
    raw_capture.capture_assistant_turn(
        tmp_path,
        {"last_assistant_message": "Sure, I'll style the buttons.", "turn_id": "t1"},
    )
    result = raw_mine.mine_raw(tmp_path, dry_run=False)
    assert result["ok"] is True
    assert result["mined"] >= 1
    notes_dir = state.ensure_project_layout(tmp_path)["memory"] / "notes"
    mine_notes = list(notes_dir.glob("mine-*.md"))
    assert mine_notes, "expected at least one mined note"
    body = mine_notes[0].read_text(encoding="utf-8")
    assert 'source: "script:raw_mine"' in body
    assert "raw_pointer:" in body
    assert "blue theme" in body or "always use" in body.lower()


def test_mine_detect_plain_chat_empty():
    assert raw_mine.detect_mine_hits("how does this page look?", role="user") == []


def test_mine_detect_never_use():
    hits = raw_mine.detect_mine_hits("Never use popups on mobile.", role="user")
    assert hits
    assert hits[0]["kind"] == "preference"


def test_mine_cursor_skips_already_read(tmp_path):
    raw_capture.capture_user_prompt(
        tmp_path, {"prompt": "I prefer short answers always.", "turn_id": "a"}
    )
    first = raw_mine.mine_raw(tmp_path)
    assert first["mined"] >= 1
    second = raw_mine.mine_raw(tmp_path)
    assert second["mined"] == 0


def test_session_start_path_does_not_dump_raw(tmp_path):
    """Raw grows; load_session recall still notes-only (no full chat dump)."""
    import load_session

    raw_capture.capture_user_prompt(
        tmp_path, {"prompt": "always ask before deleting files", "turn_id": "x"}
    )
    raw_capture.capture_assistant_turn(
        tmp_path,
        {
            "last_assistant_message": "Understood. I will ask first." * 50,
            "turn_id": "x",
        },
    )
    lessons, _ = load_session.recall_memory_notes(tmp_path)
    blob = "\n".join(lessons)
    # Full assistant dump must not appear in recall inject material.
    assert "Understood. I will ask first." * 10 not in blob
