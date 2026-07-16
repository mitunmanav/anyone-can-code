import json
import sys
from pathlib import Path
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import front_door
import canonical_state
import status_model
import safety_receipts


def test_idea_routes_through_front_door_and_updates_state(tmp_path):
    result = front_door.run_front_door("build me a todo app")
    assert result.get("mode") == "idea"
    assert "route" in result
    assert "banner" in result

    state_path = tmp_path / ".codex" / "anyone-can-code" / "state" / "workflow.json"
    canonical_state.write_state(
        tmp_path,
        active_goal="build a todo app",
        active_task="intake",
        next_action="Ask: who uses it?",
    )
    state = json.loads(state_path.read_text())
    assert state["active_goal"] == "build a todo app"
    assert state["next_action"] == "Ask: who uses it?"


def test_verify_blocks_done_without_evidence(tmp_path):
    with pytest.raises(ValueError, match="Verified state requires evidence"):
        status_model.build_observability(
            route="execute -> verify",
            states={"build": "verified"},
            next_step="ship it",
            evidence=[],
        )


def test_safety_gate_blocks_risky_action_without_approval():
    action = {"type": "delete", "command": "rm -rf /tmp/project"}
    classification = safety_receipts.classify_action(action)
    assert classification["approval_required"] is True
    result = safety_receipts.validate_action_authority(action)
    assert result["missing"]


def test_resume_reads_canonical_state(tmp_path):
    canonical_state.write_state(
        tmp_path,
        active_goal="continue refactor",
        active_task="implement auth",
        next_action="Run tests.",
    )
    state = canonical_state.read_state(tmp_path)
    assert state["active_goal"] == "continue refactor"
    assert "phase" not in state or state.get("phase") in (None, "", "idle")
