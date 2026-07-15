#!/usr/bin/env python3
"""Item 18: user always SEES what the AI did — plain receipt from local journals.

CHEAP: reads tool-usage.jsonl + signal log written by hooks. No AI call.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_jsonl(path: Path, limit: int = 30) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def project_journals(repo_root: Path) -> dict[str, Path]:
    base = Path(repo_root) / ".codex" / "anyone-can-code" / "state"
    return {
        "tools": base / "tool-usage.jsonl",
        "signals": base / "signals.jsonl",
    }


def build_plain_receipt(repo_root: Path, *, limit: int = 8) -> dict[str, Any]:
    """Short plain list of recent AI tool actions."""
    paths = project_journals(repo_root)
    tools = _read_jsonl(paths["tools"], limit=40)
    lines: list[str] = []
    for row in tools[-limit:]:
        name = str(row.get("tool_name") or "tool")
        preview = str(row.get("command_preview") or "").strip()
        if preview:
            lines.append(f"- Used {name}: {preview[:100]}")
        else:
            lines.append(f"- Used {name}")
    if not lines:
        return {
            "count": 0,
            "lines": ["- No tool actions recorded yet this project."],
            "user_block": "What AI did: nothing recorded yet.",
        }
    block = "What AI did (recent):\n" + "\n".join(lines)
    return {"count": len(lines), "lines": lines, "user_block": block}
