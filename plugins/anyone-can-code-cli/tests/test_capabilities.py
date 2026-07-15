"""Improvement loop item 21 (user order): runtime capability registry.

Registry lives in runtime state (.codex/anyone-can-code/capabilities.json),
NOT in plugin files — a new Codex feature added there reaches session context
without any plugin re-release.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import capabilities
import state


def test_defaults_seeded_and_injected(tmp_path):
    import load_session

    ctx = load_session.build_context(tmp_path, "startup")
    assert "Codex features" in ctx
    assert "worktree" in ctx.lower()


def test_fake_registry_entry_appears_in_session_context(tmp_path):
    import load_session

    reg = capabilities.registry_path(tmp_path)
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        json.dumps({"features": [{"name": "holo-deck", "route": "new Codex feature"}]}),
        encoding="utf-8",
    )
    ctx = load_session.build_context(tmp_path, "startup")
    assert "holo-deck" in ctx, "registry entry must reach context with no plugin edit"


def test_registry_lives_in_runtime_state_not_plugin(tmp_path):
    reg = capabilities.registry_path(tmp_path)
    assert str(state.project_root(tmp_path)) in str(reg)
    assert "plugins" not in str(reg.relative_to(tmp_path))


def test_capability_line_capped(tmp_path):
    reg = capabilities.registry_path(tmp_path)
    reg.parent.mkdir(parents=True, exist_ok=True)
    features = [{"name": f"feature-{i}-{'x'*30}", "route": "y" * 50} for i in range(30)]
    reg.write_text(json.dumps({"features": features}), encoding="utf-8")
    line = capabilities.capability_line(tmp_path)
    assert len(line) <= capabilities.LINE_MAX


def test_broken_registry_falls_back_to_defaults(tmp_path):
    reg = capabilities.registry_path(tmp_path)
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text("{not json", encoding="utf-8")
    line = capabilities.capability_line(tmp_path)
    assert "worktree" in line.lower()
