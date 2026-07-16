"""Runtime capability registry (user order 2026-07-07): the list of Codex
features ACC routes to lives in runtime state, not plugin files. A new Codex
feature added to capabilities.json reaches session context with zero plugin
edits. Doc-verified defaults from offical-codex-docs app/*."""

from __future__ import annotations

import json
from pathlib import Path

import state

LINE_MAX = 240

DEFAULT_FEATURES = [
    {"name": "integrated terminal", "route": "Cmd+J, read live output"},
    {"name": "review pane", "route": "green added, red removed, revert per file"},
    {"name": "worktree threads", "route": "safe copy, Handoff back"},
    {"name": "cloud threads", "route": "remote background, laptop can sleep"},
    {"name": "automations", "route": "scheduled prompts"},
    {"name": "voice dictation", "route": "Ctrl+M"},
    {"name": "in-app browser", "route": "@Browser, Ctrl+Shift+B"},
    {"name": "local actions", "route": "one-click buttons in app Settings"},
]


def registry_path(repo_root: Path) -> Path:
    return state.project_root(repo_root) / "capabilities.json"


def load_features(repo_root: Path) -> list[dict]:
    """Registry wins; defaults seed the file on first run."""
    reg = registry_path(repo_root)
    if reg.exists():
        try:
            data = json.loads(reg.read_text(encoding="utf-8"))
            features = data.get("features")
            if isinstance(features, list) and features:
                return features
        except (OSError, json.JSONDecodeError):
            return list(DEFAULT_FEATURES)
    try:
        reg.parent.mkdir(parents=True, exist_ok=True)
        reg.write_text(
            json.dumps({"features": DEFAULT_FEATURES}, indent=1), encoding="utf-8"
        )
    except OSError:
        pass
    return list(DEFAULT_FEATURES)


def capability_line(repo_root: Path) -> str:
    """One capped line naming what Codex offers, so skills route, not rebuild."""
    names = [str(f.get("name", "")).strip() for f in load_features(repo_root)]
    names = [n for n in names if n]
    if not names:
        return ""
    line = "Codex features here — route to them, never rebuild: " + ", ".join(names) + "."
    return line[:LINE_MAX]
