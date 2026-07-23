"""Feature matrix row definitions for ACC CLI blind proof."""
from __future__ import annotations

from copy import deepcopy

SKILL_ROWS = [
    "setup",
    "help",
    "status",
    "resume",
    "verify",
    "fix",
    "onboard",
    "clarify",
    "plan",
    "execute",
    "learn",
    "wiki",
    "capture",
    "govern",
    "readable",
    "handoff",
    "bridge",
    "settings",
    "update",
    "usage",
    "orchestrator",
]

HOOK_ROWS = [
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "Stop",
    "PreCompact",
    "SubagentStart",
    "SubagentStop",
    "PostCompact",
]

OTHER_ROWS = [
    "doctor",
    "memory_write",
    "memory_recall",
    "safety_curl_pipe",
    "portable_handoff",
]


def all_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    rows.extend((r, "skill") for r in SKILL_ROWS)
    rows.extend((r, "hook") for r in HOOK_ROWS)
    rows.extend((r, "other") for r in OTHER_ROWS)
    return rows


def empty_scoreboard() -> dict[str, dict[str, str]]:
    sb: dict[str, dict[str, str]] = {}
    for name, kind in all_rows():
        sb[name] = {
            "kind": kind,
            "status": "NOT PROVEN",
            "evidence": "",
            "notes": "",
        }
    return sb


def clone_scoreboard(sb: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    return deepcopy(sb)
