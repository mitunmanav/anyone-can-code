"""Compare the running plugin version against the installed cache; nudge in plain words."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _parse(version: str) -> tuple:
    parts = re.findall(r"\d+", version)
    return tuple(int(p) for p in parts[:4]) if parts else (0,)


def source_version(plugin_root: Path | None = None) -> str:
    root = plugin_root or Path(__file__).resolve().parents[2]
    manifest = root / ".codex-plugin" / "plugin.json"
    try:
        return str(json.loads(manifest.read_text(encoding="utf-8")).get("version", ""))
    except (OSError, json.JSONDecodeError):
        return ""


def cached_versions(cache_root: Path | None = None) -> list[str]:
    root = cache_root or (Path.home() / ".codex" / "plugins" / "cache")
    if not root.exists():
        return []
    return sorted(
        version.name
        for plugin_dir in root.glob("*/anyone-can-code")
        for version in plugin_dir.iterdir()
        if version.is_dir()
    )


def update_nudge(plugin_root: Path | None = None, cache_root: Path | None = None) -> str:
    """'' when healthy; one caveman line when the install needs attention."""
    running = source_version(plugin_root)
    cached = cached_versions(cache_root)
    if not running or not cached:
        return ""
    if len(set(cached)) > 1:
        return (
            f"Plugin cache holds an old version too ({', '.join(sorted(set(cached)))}). "
            "Stale copies caused skill loss before. Remove old ones, then run $update."
        )
    newest = max(cached, key=_parse)
    if _parse(newest) > _parse(running):
        return (
            f"Plugin outdated: running {running}, installed {newest}. "
            "Restart Codex, then run $update to migrate project state."
        )
    return ""
