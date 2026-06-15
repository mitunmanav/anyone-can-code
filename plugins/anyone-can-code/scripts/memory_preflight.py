#!/usr/bin/env python3
"""Project memory recall gate for ACC front-door work."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any


PROJECT_NAMESPACE = "anyone-can-code"
DEFAULT_MEMORY_PATH = ".codex/anyone-can-code/memory/notes"
DEFAULT_LIMIT = 5
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def selected_memory_notes_path(project_root: Path) -> Path:
    preferences_path = project_root / ".codex" / PROJECT_NAMESPACE / "settings" / "preferences.json"
    preferences = read_json(preferences_path) or {}
    raw = Path(str(preferences.get("memory_path") or DEFAULT_MEMORY_PATH)).expanduser()
    return raw if raw.is_absolute() else project_root / raw


def selected_memory_root(project_root: Path) -> Path:
    return selected_memory_notes_path(project_root).resolve().parent


def load_memory_server():
    path = PLUGIN_ROOT / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("acc_memory_preflight_server", path)
    if not spec or not spec.loader:
        raise RuntimeError("Memory server could not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def with_memory_root(project_root: Path, callback):
    old_root = os.environ.get("ACC_MCP_DATA_ROOT")
    os.environ["ACC_MCP_DATA_ROOT"] = str(selected_memory_root(project_root))
    try:
        return callback(load_memory_server())
    finally:
        if old_root is None:
            os.environ.pop("ACC_MCP_DATA_ROOT", None)
        else:
            os.environ["ACC_MCP_DATA_ROOT"] = old_root


def retrieve_relevant_memory(
    project_root: Path,
    request: str,
    *,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    query = str(request).strip()
    if not query:
        raise ValueError("request required")
    project_root = project_root.resolve()
    safe_limit = max(1, min(int(limit or DEFAULT_LIMIT), DEFAULT_LIMIT))

    result = with_memory_root(
        project_root,
        lambda server: server.retrieve_context(
            {"query": query, "project_root": str(project_root), "limit": safe_limit}
        ),
    )
    items = result.get("items", [])
    count = len(items) if isinstance(items, list) else 0
    return {
        "status": "ready",
        "mode": "portable-markdown",
        "project_root": str(project_root),
        "memory_root": str(selected_memory_root(project_root)),
        "query": query,
        "limit": safe_limit,
        "used": count > 0,
        "count": count,
        "items": items if isinstance(items, list) else [],
        "visible_line": (
            f"Relevant memory used: {count} item(s)"
            if count
            else "Relevant memory used: none found"
        ),
        "required_before": [
            "ask-question",
            "plan",
            "route-specialist",
            "browser-action",
            "server-action",
            "tool-action",
        ],
    }


def store_learned_memory(
    project_root: Path,
    summary: str,
    *,
    scope: str = "project",
    kind: str = "mistake",
    source: str = "user-correction",
    confidence: float = 0.8,
    evidence: str = "",
) -> dict[str, Any]:
    project_root = project_root.resolve()
    payload = {
        "project_root": str(project_root),
        "scope": scope,
        "kind": kind,
        "summary": summary,
        "source": source,
        "confidence": confidence,
        "evidence": evidence,
    }
    result = with_memory_root(project_root, lambda server: server.store_feedback(payload))
    record = result.get("record", {})
    return {
        "stored": bool(result.get("stored")),
        "mode": result.get("mode", "portable-markdown"),
        "id": record.get("id"),
        "path": result.get("path"),
        "scope": record.get("scope"),
        "kind": record.get("kind"),
        "summary": record.get("summary"),
    }


def smoke_check() -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        notes = project_root / ".codex" / PROJECT_NAMESPACE / "memory" / "notes"
        settings = project_root / ".codex" / PROJECT_NAMESPACE / "settings"
        settings.mkdir(parents=True)
        settings.joinpath("preferences.json").write_text(
            json.dumps({"memory_mode": "portable-markdown", "memory_path": str(notes)}),
            encoding="utf-8",
        )
        stored = store_learned_memory(
            project_root,
            "When user asks after update, recall learned plugin mistakes before choosing skills.",
            evidence="memory_preflight smoke",
        )
        recalled = retrieve_relevant_memory(
            project_root,
            "After plugin update choose skills and recall learned mistakes",
        )
    if not stored.get("stored"):
        return False, "memory store failed"
    if not recalled.get("used"):
        return False, "memory recall failed"
    if "Relevant memory used:" not in recalled.get("visible_line", ""):
        return False, "memory visible line missing"
    return True, "learned memory stored and recalled before first action"


def main() -> None:
    parser = argparse.ArgumentParser(description="ACC memory preflight")
    parser.add_argument("request", help="User request to recall memory for")
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()
    print(
        json.dumps(
            retrieve_relevant_memory(Path(args.project_root), args.request, limit=args.limit),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
