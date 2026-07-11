import json
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, call

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))
import save_session
import state as hook_state

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import canonical_state


def test_active_task_not_truncated_at_160(tmp_path):
    """Test that active_task is set to 280 chars, not truncated at 160."""
    # Create a 200-character summary
    long_summary = "x" * 200

    # Set up minimal state
    canonical_state.write_state(tmp_path, active_task="")

    payload = {
        "last_assistant_message": long_summary,
        "turn_id": "test-turn-1",
        "hook_event_name": "Stop",
    }

    save_session.handle_payload(payload, tmp_path)

    # Read the workflow state to verify active_task
    workflow = canonical_state.read_state(tmp_path)
    assert len(workflow.get("active_task", "")) == 200, (
        f"active_task should be 200 chars, but got {len(workflow.get('active_task', ''))} chars: "
        f"{workflow.get('active_task', '')}"
    )


def test_long_summary_not_chopped_at_280(tmp_path):
    """BUG-1 (audit v2): multi-step instructions must survive into active_task."""
    steps = "Go to Supabase dashboard and check the schema table. " * 20  # ~1080 chars
    canonical_state.write_state(tmp_path, active_task="")

    payload = {
        "last_assistant_message": steps,
        "turn_id": "test-turn-bug1",
        "hook_event_name": "Stop",
    }

    save_session.handle_payload(payload, tmp_path)

    workflow = canonical_state.read_state(tmp_path)
    assert workflow.get("active_task", "") == steps, (
        f"active_task chopped: {len(workflow.get('active_task', ''))} chars kept "
        f"of {len(steps)}"
    )


def test_summary_truncates_on_word_boundary():
    """BUG-1 (audit v2): oversize summaries cut at a word boundary, never mid-word."""
    text = "word " * 800  # 4000 chars
    result = save_session.session_summary({"last_assistant_message": text})
    assert result.endswith("...")
    assert len(result) <= save_session.SUMMARY_MAX_CHARS + 3
    body = result[:-3].rstrip()
    assert body.endswith("word"), f"mid-word cut: ...{body[-10:]!r}"


def test_write_state_retries_transaction_error(tmp_path):
    """BUG-2 (audit v2): one transient StateTransactionError must not lose the save."""
    real = canonical_state.update_canonical_state
    calls = {"n": 0}

    def flaky(root, updates, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise canonical_state.StateTransactionError("transient lock")
        return real(root, updates, **kwargs)

    with patch.object(hook_state.canonical_state, "update_canonical_state", side_effect=flaky), \
            patch.object(hook_state.time, "sleep"):
        result = hook_state.write_state(tmp_path, {"active_task": "retry works"})

    assert calls["n"] == 2, f"expected 1 retry, got {calls['n']} attempts"
    assert result.get("active_task") == "retry works"


def test_write_state_raises_after_retry_budget(tmp_path):
    """BUG-2 (audit v2): persistent failure still surfaces, no silent loss."""
    with patch.object(
        hook_state.canonical_state,
        "update_canonical_state",
        side_effect=canonical_state.StateTransactionError("disk gone"),
    ) as mock_update, patch.object(hook_state.time, "sleep"):
        with pytest.raises(canonical_state.StateTransactionError):
            hook_state.write_state(tmp_path, {"active_task": "never lands"})

    assert mock_update.call_count == hook_state.STATE_WRITE_ATTEMPTS


def test_handle_payload_calls_write_session_snapshot(tmp_path):
    """Test that handle_payload calls write_session_snapshot with correct args."""
    # Set up minimal state
    canonical_state.write_state(tmp_path, active_task="")

    payload = {
        "last_assistant_message": "Test message",
        "turn_id": "test-turn-1",
        "hook_event_name": "Stop",
    }

    with patch.object(save_session, "write_session_snapshot") as mock_snapshot:
        save_session.handle_payload(payload, tmp_path)

        # Verify write_session_snapshot was called
        assert mock_snapshot.called, "write_session_snapshot should be called"
        # Verify it was called with correct arguments
        args, kwargs = mock_snapshot.call_args
        assert args[0] == tmp_path, "First arg should be repo_root"
        assert isinstance(args[1], str), "Second arg should be summary string"
        assert isinstance(args[2], dict), "Third arg should be workflow dict"


def test_memory_notes_written_to_disk_without_mcp(tmp_path, monkeypatch):
    """When MCP server unavailable, learning must be written to memory/notes/ on disk."""
    import state as hook_state
    monkeypatch.setenv("PLUGIN_ROOT", "")  # force MCP unavailable
    signals = [
        {"signal_type": "manual_learn", "detail": "Always use real DB for deploys", "timestamp": "2026-06-24T10:00:00Z"},
    ]
    save_session.durable_memory_writes(tmp_path, signals, "session ended cleanly")
    from datetime import date
    notes_dir = hook_state.ensure_project_layout(tmp_path)["memory"] / "notes"
    today = date.today().isoformat()
    note_file = notes_dir / f"{today}.md"
    assert note_file.exists(), f"Expected {note_file} to exist"
    content = note_file.read_text()
    assert "Always use real DB for deploys" in content


def test_handle_payload_creates_session_snapshot(tmp_path):
    """Test that handle_payload actually creates the session snapshot file."""
    # Set up minimal state
    canonical_state.write_state(tmp_path, active_task="")

    payload = {
        "last_assistant_message": "Test implementation",
        "turn_id": "test-turn-2",
        "hook_event_name": "Stop",
    }

    save_session.handle_payload(payload, tmp_path)

    # Verify the snapshot file was created
    snapshot_path = tmp_path / ".codex" / "anyone-can-code" / "state" / "session-snapshot.md"
    assert snapshot_path.exists(), f"Session snapshot file should exist at {snapshot_path}"

    # Verify content
    content = snapshot_path.read_text(encoding="utf-8")
    assert "# Anyone Can Code - Session Snapshot" in content
    assert "Test implementation" in content
    assert "Workflow Snapshot" in content


def test_memory_write_proof_recorded(tmp_path):
    """Backlog 3: durable memory writes must leave a proof field in state."""
    canonical_state.write_state(tmp_path, active_task="")
    hook_state.append_jsonl(
        hook_state.signal_log_path(tmp_path),
        {"timestamp": "2026-07-06T10:00:00Z",
         "signal_type": "manual_learn",
         "detail": "Ship only after verify"},
    )

    save_session.handle_payload(
        {"last_assistant_message": "done", "turn_id": "t1", "hook_event_name": "Stop"},
        tmp_path,
    )

    workflow = canonical_state.read_state(tmp_path)
    assert workflow.get("memory_write_proof"), "memory_write_proof still empty"
