"""Improvement loop item 3: every spawned subagent auto-gets rules; results logged.

Doc-verified (core/hooks.md): SubagentStart supports additionalContext;
SubagentStop carries agent_type + last_assistant_message.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import subagent
import state


def test_subagent_start_injects_caveman_and_scope(tmp_path):
    result = subagent.handle_payload(
        {"hook_event_name": "SubagentStart", "agent_type": "explore", "agent_id": "a1"},
        tmp_path,
    )
    out = result["hookSpecificOutput"]
    assert out["hookEventName"] == "SubagentStart"
    ctx = out["additionalContext"].lower()
    assert "caveman" in ctx
    assert "job" in ctx or "scope" in ctx
    assert len(out["additionalContext"]) <= 400


def test_subagent_stop_logs_signal(tmp_path):
    result = subagent.handle_payload(
        {
            "hook_event_name": "SubagentStop",
            "agent_type": "explore",
            "agent_id": "a1",
            "last_assistant_message": "found 3 routes in src/api",
        },
        tmp_path,
    )
    assert result == {}
    signals = state.read_recent_jsonl(state.signal_log_path(tmp_path), limit=5)
    assert any(s.get("signal_type") == "subagent_result" for s in signals)


def test_hooks_json_wires_subagent_events():
    config = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hooks = config["hooks"]
    assert "SubagentStart" in hooks
    assert "SubagentStop" in hooks
