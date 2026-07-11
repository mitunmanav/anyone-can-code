#!/usr/bin/env python3
"""Derived capability registry with health probes and ACC fallbacks."""

from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Any


HEALTHY = {"healthy", "available"}
UNHEALTHY = {"unhealthy", "unavailable", "missing", "failed"}


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def capability_entry(plugin: dict[str, Any]) -> dict[str, Any]:
    name = str(plugin.get("name") or "").strip().lower()
    return {
        "id": f"plugin:{name}" if name else "plugin:unknown",
        "provider": name,
        "description": str(plugin.get("description") or "").strip(),
        "skills": copy.deepcopy(plugin.get("skills") or []),
        "capability_text": str(plugin.get("capability_text") or "").strip(),
        "source": {
            "type": "installed-plugin-manifest",
            "path": str(plugin.get("manifest") or ""),
        },
        "health": {
            "status": "unknown",
            "checked_at": "",
            "reason": "not-probed",
        },
        "fallback": {
            "owner": "acc",
            "route": "local-acc",
            "reason": "capability-unavailable",
        },
        "workflow_owner": "acc",
        "durable_truth": False,
        "_plugin": plugin,
    }


def probe_capability(entry: dict[str, Any]) -> dict[str, Any]:
    checked = copy.deepcopy(entry)
    plugin = checked.pop("_plugin", {})
    status = str(plugin.get("health") or "").strip().lower()
    reason = str(plugin.get("health_reason") or "").strip()
    probe = plugin.get("health_probe")

    if callable(probe):
        try:
            result = probe(copy.deepcopy(plugin))
            if isinstance(result, dict):
                status = str(result.get("status") or "").strip().lower()
                reason = str(result.get("reason") or "").strip()
            else:
                status = "healthy" if result else "unhealthy"
                reason = "custom-probe"
        except Exception as exc:
            status = "unhealthy"
            reason = f"probe-error: {type(exc).__name__}"

    manifest = checked["source"]["path"]
    manifest_path = Path(manifest) if manifest else None
    if status not in HEALTHY | UNHEALTHY:
        if not checked["provider"] or not checked["capability_text"]:
            status = "unavailable"
            reason = "capability metadata missing"
        elif manifest_path and manifest_path.is_absolute() and not manifest_path.is_file():
            status = "unavailable"
            reason = "installed manifest missing"
        else:
            status = "healthy"
            reason = "manifest metadata readable"

    checked["health"] = {
        "status": "healthy" if status in HEALTHY else "unhealthy",
        "checked_at": utc_now(),
        "reason": reason or status,
    }
    return checked


def build_capability_registry(
    plugins: list[dict[str, Any]],
    *,
    probe: bool = True,
) -> list[dict[str, Any]]:
    registry = []
    for plugin in plugins:
        entry = capability_entry(plugin)
        registry.append(probe_capability(entry) if probe else entry)
    return registry
