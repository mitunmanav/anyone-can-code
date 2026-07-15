import json
import sys
from pathlib import Path
import pytest

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))
import load_session
import state as hook_state

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import canonical_state


def test_load_session_emits_caveman_strict_by_default(tmp_path):
    prefs_path = tmp_path / ".codex" / "anyone-can-code" / "settings" / "preferences.json"
    prefs_path.parent.mkdir(parents=True, exist_ok=True)
    prefs_path.write_text(json.dumps({}))  # no explicit mode set

    context = load_session.build_context(tmp_path, "startup")
    assert "caveman-strict" in context


def test_save_session_writes_canonical_state(tmp_path):
    canonical_state.write_state(
        tmp_path,
        active_goal="test goal",
        active_task="run tests",
        next_action="Deploy.",
    )
    payload = {
        "last_assistant_message": "Tests passed. Deploying next.",
        "hook_event_name": "Stop",
    }
    state_after = canonical_state.read_state(tmp_path)
    assert state_after["active_goal"] == "test goal"


def test_hook_state_reads_communication_mode(tmp_path):
    prefs = hook_state.read_preferences(tmp_path)
    mode = prefs.get("communication_mode", "caveman-strict")
    assert mode == "caveman-strict"
