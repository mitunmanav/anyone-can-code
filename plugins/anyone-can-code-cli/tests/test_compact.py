"""Item 12: compaction announce + PostCompact re-inject.

Doc-verified (hooks): PreCompact/PostCompact support systemMessage.
PostCompact has no additionalContext in docs — re-inject via systemMessage.
SessionStart source=compact still re-anchors in context.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import compact
import load_session
import state


def test_precompact_writes_capsule_and_announces(tmp_path):
    state.write_state(tmp_path, {"active_goal": "build waitlist site", "next_action": "add form"})
    result = compact.handle_payload(
        {"hook_event_name": "PreCompact", "trigger": "auto", "turn_id": "t1"}, tmp_path
    )
    assert "systemMessage" in result
    assert "shrink" in result["systemMessage"].lower() or "compact" in result["systemMessage"].lower()
    capsule = state.ensure_project_layout(tmp_path)["state"] / "compact-capsule.md"
    text = capsule.read_text(encoding="utf-8")
    assert "build waitlist site" in text
    assert "add form" in text


def test_postcompact_reinjects_goal_next(tmp_path):
    state.write_state(
        tmp_path,
        {"active_goal": "build waitlist site", "next_action": "add form"},
    )
    compact.handle_payload(
        {"hook_event_name": "PreCompact", "trigger": "auto"}, tmp_path
    )
    result = compact.handle_payload(
        {"hook_event_name": "PostCompact", "trigger": "auto", "turn_id": "t2"},
        tmp_path,
    )
    msg = result.get("systemMessage", "").lower()
    assert "shortened" in msg or "compact" in msg
    assert "waitlist" in msg
    assert "form" in msg
    assert "re-ask" in msg or "answered" in msg


def test_session_start_compact_reanchors(tmp_path):
    state.write_state(tmp_path, {"active_goal": "build waitlist site"})
    ctx = load_session.build_context(tmp_path, "compact")
    assert "compact" in ctx.lower()
    assert "build waitlist site" in ctx


def test_hooks_json_wires_pre_and_post_compact():
    config = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hooks = config["hooks"]
    assert "PreCompact" in hooks, "PreCompact hook missing"
    assert "PostCompact" in hooks, "PostCompact hook missing"
    session_matcher = hooks["SessionStart"][0]["matcher"]
    assert "compact" in session_matcher, "SessionStart must match source=compact"
