#!/usr/bin/env python3
"""
Runtime truth helper for Anyone Can Code.
"""

from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path


PROJECT_NAMESPACE = "anyone-can-code"
PLUGIN_NAME = "anyone-can-code"


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_toml(path: Path) -> dict | None:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None


def read_manifest_version(root: Path | None) -> str | None:
    if root is None:
        return None
    data = read_json(root / ".codex-plugin" / "plugin.json")
    if not data:
        return None
    value = data.get("version")
    return str(value) if value else None


def read_manifest_name(root: Path | None) -> str | None:
    if root is None:
        return None
    data = read_json(root / ".codex-plugin" / "plugin.json")
    if not data:
        return None
    value = data.get("name")
    return str(value) if value else None


def install_state_version(project_root: Path) -> str | None:
    data = read_json(project_root / ".codex" / PROJECT_NAMESPACE / "state" / "install.json")
    if not data:
        return None
    value = data.get("plugin_version")
    return str(value) if value else None


def version_key(value: str | None) -> tuple[int, int, int, str]:
    if not value:
        return (0, 0, 0, "")
    base_value = str(value).split("+", 1)[0]
    parts = base_value.split(".")
    numbers: list[int] = []
    suffix = ""
    for part in parts[:3]:
        digits = ""
        tail = ""
        for char in part:
            if char.isdigit() and not tail:
                digits += char
            else:
                tail += char
        numbers.append(int(digits or "0"))
        if tail and not suffix:
            suffix = tail
    while len(numbers) < 3:
        numbers.append(0)
    return (numbers[0], numbers[1], numbers[2], suffix)


def compare_versions(left: str | None, right: str | None) -> int:
    left_key = version_key(left)
    right_key = version_key(right)
    if left_key < right_key:
        return -1
    if left_key > right_key:
        return 1
    return 0


def find_marketplace_root(project_root: Path) -> Path | None:
    for candidate in [project_root, *project_root.parents]:
        marketplace = candidate / ".agents" / "plugins" / "marketplace.json"
        if marketplace.exists():
            return candidate
    return None


def resolve_plugin_source_root(marketplace_root: Path | None, plugin_name: str) -> Path | None:
    if marketplace_root is None:
        return None
    marketplace_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    payload = read_json(marketplace_path)
    if not payload:
        return None
    plugins = payload.get("plugins", [])
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("name", "")).strip() != plugin_name:
            continue
        source = entry.get("source")
        if isinstance(source, str):
            path_value = source
        elif isinstance(source, dict):
            if str(source.get("source", "")).strip() != "local":
                continue
            path_value = str(source.get("path", "")).strip()
        else:
            continue
        if not path_value.startswith("./"):
            continue
        resolved = (marketplace_root / path_value).resolve()
        try:
            resolved.relative_to(marketplace_root.resolve())
        except ValueError:
            continue
        return resolved
    return None


def codex_home() -> Path:
    root = os.environ.get("CODEX_HOME")
    if root:
        return Path(root)
    return Path.home() / ".codex"


def configured_marketplace(marketplace_root: Path | None) -> dict:
    if marketplace_root is None:
        return {
            "name": None,
            "configured": False,
            "source": None,
            "source_type": None,
            "upgrade_mode": "none",
        }

    marketplace_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    payload = read_json(marketplace_path) or {}
    marketplace_name = str(payload.get("name", "")).strip() or None
    config = read_toml(codex_home() / "config.toml") or {}
    entry = (config.get("marketplaces") or {}).get(marketplace_name or "", {})
    source_type = entry.get("source_type")
    source = entry.get("source")
    configured = bool(entry)
    upgrade_mode = "none"
    if configured:
        upgrade_mode = "git" if source_type == "git" else "local"
    return {
        "name": marketplace_name,
        "configured": configured,
        "source": str(source) if source else None,
        "source_type": str(source_type) if source_type else None,
        "upgrade_mode": upgrade_mode,
    }


def find_installed_plugin_root(plugin_name: str, plugin_root: Path) -> Path | None:
    if "plugins" in plugin_root.parts and "cache" in plugin_root.parts:
        return plugin_root

    cache_root = codex_home() / "plugins" / "cache"
    if not cache_root.exists():
        return None

    candidates: list[tuple[tuple[int, int, int, str], Path]] = []
    for manifest in cache_root.glob(f"*/*/*/.codex-plugin/plugin.json"):
        root = manifest.parent.parent
        if read_manifest_name(root) != plugin_name:
            continue
        candidates.append((version_key(read_manifest_version(root)), root))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def find_wrong_root_hint(project_root: Path) -> Path | None:
    for child in project_root.iterdir():
        if not child.is_dir():
            continue
        marker = child / ".agents" / "plugins" / "marketplace.json"
        if marker.exists():
            return child
    return None


def build_runtime_info(project_root: Path, plugin_root: Path) -> dict:
    plugin_name = read_manifest_name(plugin_root) or PLUGIN_NAME
    marketplace_root = find_marketplace_root(project_root)
    marketplace_config = configured_marketplace(marketplace_root)
    source_root = resolve_plugin_source_root(marketplace_root, plugin_name)
    installed_root = find_installed_plugin_root(plugin_name, plugin_root)
    project_version = install_state_version(project_root)
    source_version = read_manifest_version(source_root)
    runtime_version = read_manifest_version(installed_root)
    wrong_root_hint = None
    if marketplace_root is None:
        wrong_root_hint = find_wrong_root_hint(project_root)

    info = {
        "project_root": str(project_root),
        "marketplace_root": str(marketplace_root) if marketplace_root else None,
        "marketplace_name": marketplace_config["name"],
        "managed_marketplace_configured": marketplace_config["configured"],
        "managed_marketplace_source": marketplace_config["source"],
        "managed_marketplace_source_type": marketplace_config["source_type"],
        "marketplace_upgrade_mode": marketplace_config["upgrade_mode"],
        "plugin_source_root": str(source_root) if source_root else None,
        "installed_plugin_root": str(installed_root) if installed_root else None,
        "project_state_version": project_version,
        "plugin_source_version": source_version,
        "installed_runtime_version": runtime_version,
        "can_migrate": False,
        "next_action": "unknown",
        "wrong_root_hint": str(wrong_root_hint) if wrong_root_hint else None,
    }

    if source_root is None and installed_root is None:
        info["next_action"] = "missing-runtime-and-source"
        return info
    if installed_root is None:
        info["next_action"] = "refresh-plugin-first"
        return info
    if source_root is not None and compare_versions(source_version, runtime_version) > 0:
        info["next_action"] = "refresh-plugin-first"
        return info
    if compare_versions(project_version, runtime_version) < 0:
        info["can_migrate"] = True
        info["next_action"] = "migrate-project"
        return info
    if compare_versions(project_version, runtime_version) > 0:
        info["next_action"] = "project-ahead-of-runtime"
        return info
    if source_root is not None and compare_versions(source_version, runtime_version) < 0:
        info["next_action"] = "runtime-ahead-of-source"
        return info
    info["next_action"] = "same-everywhere"
    return info
