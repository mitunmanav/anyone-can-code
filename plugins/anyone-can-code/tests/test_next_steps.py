"""Backlog 7: structured next_steps[] replaces free-text next-action prose.

Audit rec #1 end state: workflow.json carries a structured step list, the
capsule renders it, and next_action stays honest (first pending step).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import canonical_state


def test_default_state_has_next_steps():
    assert canonical_state.DEFAULT_STATE["next_steps"] == []


def test_string_steps_normalized_to_dicts(tmp_path):
    state = canonical_state.update_canonical_state(
        tmp_path, {"next_steps": ["run tests", "fix login bug"]}
    )
    assert state["next_steps"] == [
        {"step": "run tests", "status": "pending"},
        {"step": "fix login bug", "status": "pending"},
    ]


def test_dict_steps_kept_and_garbage_dropped(tmp_path):
    state = canonical_state.update_canonical_state(
        tmp_path,
        {"next_steps": [
            {"step": "deploy", "status": "done"},
            {"step": "verify deploy"},
            42,
            {"nonsense": True},
        ]},
    )
    assert state["next_steps"] == [
        {"step": "deploy", "status": "done"},
        {"step": "verify deploy", "status": "pending"},
    ]


def test_next_action_falls_back_to_first_pending_step(tmp_path):
    state = canonical_state.update_canonical_state(
        tmp_path,
        {"next_steps": [
            {"step": "deploy", "status": "done"},
            {"step": "verify deploy", "status": "pending"},
        ]},
    )
    assert state["next_action"] == "verify deploy"


def test_explicit_next_action_wins(tmp_path):
    state = canonical_state.update_canonical_state(
        tmp_path,
        {"next_action": "ship it", "next_steps": ["something else"]},
    )
    assert state["next_action"] == "ship it"


def test_capsule_carries_and_renders_next_steps(tmp_path):
    canonical_state.update_canonical_state(
        tmp_path,
        {"next_steps": [
            {"step": "deploy", "status": "done"},
            {"step": "verify deploy", "status": "pending"},
        ]},
    )
    state = canonical_state.read_canonical_state(tmp_path)
    assert state["active_task_capsule"]["next_steps"] == state["next_steps"]

    capsule_md = (
        canonical_state.state_paths(tmp_path)["capsule"].read_text(encoding="utf-8")
    )
    assert "## Next Steps" in capsule_md
    assert "[x] deploy" in capsule_md
    assert "[ ] verify deploy" in capsule_md
