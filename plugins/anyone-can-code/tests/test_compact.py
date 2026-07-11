"""Improvement loop item 2: long sessions survive compaction.

Doc-verified (core/hooks.md): PreCompact runs before compaction (save the
capsule); PostCompact has NO additionalContext channel, but SessionStart
fires with source "compact" and DOES — so re-anchoring rides SessionStart.
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


def test_precompact_writes_capsule(tmp_path):
    state.write_state(tmp_path, {"active_goal": "build waitlist site", "next_action": "add form"})
    result = compact.handle_payload(
        {"hook_event_name": "PreCompact", "trigger": "auto", "turn_id": "t1"}, tmp_path
    )
    assert result == {}
    capsule = state.ensure_project_layout(tmp_path)["state"] / "compact-capsule.md"
    text = capsule.read_text(encoding="utf-8")
    assert "build waitlist site" in text
    assert "add form" in text


def test_session_start_compact_reanchors(tmp_path):
    state.write_state(tmp_path, {"active_goal": "build waitlist site"})
    ctx = load_session.build_context(tmp_path, "compact")
    assert "compact" in ctx.lower()
    assert "build waitlist site" in ctx


def test_hooks_json_wires_compaction():
    config = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hooks = config["hooks"]
    assert "PreCompact" in hooks, "PreCompact hook missing"
    session_matcher = hooks["SessionStart"][0]["matcher"]
    assert "compact" in session_matcher, "SessionStart must match source=compact"
