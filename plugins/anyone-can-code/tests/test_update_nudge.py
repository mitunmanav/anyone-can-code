"""Improvement loop item 9: outdated install -> plain-words nudge at session start.

Real-trial failure: two plugin versions cached at once, skills vanished.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import version_check
import load_session


def _make_plugin(root: Path, version: str) -> Path:
    manifest = root / ".codex-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"version": version}), encoding="utf-8")
    return root


def _make_cache(root: Path, versions: list[str]) -> Path:
    for v in versions:
        (root / "marketplace" / "anyone-can-code" / v).mkdir(parents=True, exist_ok=True)
    return root


def test_no_nudge_when_versions_match(tmp_path):
    plugin = _make_plugin(tmp_path / "plugin", "1.1.0")
    cache = _make_cache(tmp_path / "cache", ["1.1.0"])
    assert version_check.update_nudge(plugin_root=plugin, cache_root=cache) == ""


def test_nudge_when_newer_version_cached(tmp_path):
    plugin = _make_plugin(tmp_path / "plugin", "1.0.0")
    cache = _make_cache(tmp_path / "cache", ["1.1.0"])
    nudge = version_check.update_nudge(plugin_root=plugin, cache_root=cache)
    assert "$update" in nudge
    assert "1.1.0" in nudge


def test_nudge_when_duplicate_versions_cached(tmp_path):
    plugin = _make_plugin(tmp_path / "plugin", "1.1.0")
    cache = _make_cache(tmp_path / "cache", ["1.0.0", "1.1.0"])
    nudge = version_check.update_nudge(plugin_root=plugin, cache_root=cache)
    assert "old version" in nudge.lower() or "stale" in nudge.lower()


def test_silent_when_no_cache(tmp_path):
    plugin = _make_plugin(tmp_path / "plugin", "1.1.0")
    assert version_check.update_nudge(plugin_root=plugin, cache_root=tmp_path / "nope") == ""


def test_session_context_carries_nudge(tmp_path, monkeypatch):
    monkeypatch.setattr(version_check, "update_nudge", lambda **kw: "Plugin outdated. Run $update.")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Run $update" in ctx
