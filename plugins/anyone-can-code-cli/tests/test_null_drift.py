import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import guard
import front_door


def test_takeover_keys_are_blocked_by_guard():
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"command": '{"workflow_owner": "foreign-plugin"}'},
    }
    result = guard.check_workflow_takeover(payload)
    assert result["blocked"] is True


def test_null_result_falls_back_to_acc():
    result = front_door.handle_null_specialist_result("foreign-skill", {})
    assert result["owner"] == "acc"
    assert result["fallback"] is True


def test_acc_keeps_workflow_owner_after_specialist():
    result = front_door.run_front_door("build an api", context={"workflow_owner": "acc"})
    assert result.get("workflow_owner", "acc") == "acc"
