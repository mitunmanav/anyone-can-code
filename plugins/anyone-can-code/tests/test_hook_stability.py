"""Stability: UTF-8 surrogates, PLUGIN_ROOT commands, encode-circuit heal."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "hooks" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(PLUGIN / "scripts"))

import memory_core  # noqa: E402
import save_session  # noqa: E402
import state  # noqa: E402


def test_safe_text_strips_lone_surrogates():
    bad = "hello \udc9d world"
    fixed = memory_core.safe_text(bad)
    fixed.encode("utf-8")  # must not raise
    assert "\udc9d" not in fixed


def test_atomic_write_survives_surrogates(tmp_path: Path):
    target = tmp_path / "note.md"
    memory_core.atomic_write_text(target, "goal \udc9d next")
    text = target.read_text(encoding="utf-8")
    assert "goal" in text
    assert "next" in text


def test_hooks_json_uses_codex_plugin_root_template():
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    for event, groups in hooks["hooks"].items():
        for group in groups:
            for hook in group.get("hooks", []):
                assert "${PLUGIN_ROOT}" in hook["command"], event
                assert "${PLUGIN_ROOT}" in hook["commandWindows"], event
                assert "%PLUGIN_ROOT%" not in hook["commandWindows"], event
                assert "$PLUGIN_ROOT" not in hook["command"].replace("${PLUGIN_ROOT}", "")


def test_encode_circuit_does_not_block_forever(tmp_path: Path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".codex" / "anyone-can-code").mkdir(parents=True)
    # Trip health with encode fail twice (old bug).
    state.record_hook_result(
        root,
        "save_session",
        "fail",
        reason="State transaction rolled back: 'utf-8' codec can't encode character '\\udc9d'",
    )
    state.record_hook_result(
        root,
        "save_session",
        "fail",
        reason="State transaction rolled back: 'utf-8' codec can't encode character '\\udc9d'",
    )
    health = state.read_hook_health(root)
    # May mark circuit_open in file, but hook_circuit_open must heal encode reasons.
    assert state.hook_circuit_open(root, "save_session") is False


def test_save_session_with_surrogate_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".codex" / "anyone-can-code").mkdir(parents=True)
    # Minimal ACC layout via ensure
    state.ensure_project_layout(root)
    payload = {
        "hook_event_name": "Stop",
        "last_assistant_message": "Done \udc9d with shiprocket.",
        "session_id": "t1",
        "turn_id": "t1",
        "cwd": str(root),
    }
    result = save_session.handle_payload(payload, root)
    assert result == {}
    now = state.ensure_project_layout(root)["memory"] / "NOW.md"
    assert now.exists()
    now.read_text(encoding="utf-8")  # must not raise
    # Circuit must not lock after encode-safe save
    assert state.hook_circuit_open(root, "save_session") is False
