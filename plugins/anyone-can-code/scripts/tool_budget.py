#!/usr/bin/env python3
"""Session tool-call budget — Cascade-style soft limit.

Windsurf/Devin Cascade: up to 20 tool calls per prompt; press continue
(or Auto-Continue) to resume. ACC mirrors with a local counter file and
soft warn only (never hard deny).

State: `.codex/anyone-can-code/state/tool-budget.json`
Used by `$tool-budget` skill + optional clean PostToolUse track via audit.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

REL_PATH = Path(".codex/anyone-can-code/state/tool-budget.json")
PREFS_PATH = Path(".codex/anyone-can-code/settings/preferences.json")
# Cascade docs: "up to 20 tool calls per prompt"
DEFAULT_LIMIT = 20
SOFT_RATIO = 0.8
SCHEMA_VERSION = 1

_EXIT_CODE_RE = re.compile(r"exit (?:code|status) (\d+)", re.I)
_STRONG_FAIL = (
    "traceback",
    "exception:",
    "error:",
    "failed",
    "command not found",
    "permission denied",
    "fatal:",
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def budget_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / REL_PATH


def _empty(limit: int = DEFAULT_LIMIT, session_id: str = "") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "count": 0,
        "limit": max(1, int(limit)),
        "segment": 1,
        "session_id": (session_id or "").strip(),
        "last_tool": "",
        "updated": _utc_now(),
    }


def load(repo_root: Path | str) -> dict[str, Any]:
    path = budget_path(repo_root)
    if not path.is_file():
        return _empty()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty()
    if not isinstance(raw, dict):
        return _empty()
    data = _empty(
        limit=int(raw.get("limit") or DEFAULT_LIMIT),
        session_id=str(raw.get("session_id") or ""),
    )
    try:
        data["count"] = max(0, int(raw.get("count") or 0))
    except (TypeError, ValueError):
        data["count"] = 0
    try:
        data["segment"] = max(1, int(raw.get("segment") or 1))
    except (TypeError, ValueError):
        data["segment"] = 1
    data["last_tool"] = str(raw.get("last_tool") or "")[:80]
    data["updated"] = str(raw.get("updated") or data["updated"])
    return data


def _write(repo_root: Path | str, data: dict[str, Any]) -> Path:
    path = budget_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(data)
    payload["schema_version"] = SCHEMA_VERSION
    payload["updated"] = _utc_now()
    payload["count"] = max(0, int(payload.get("count") or 0))
    payload["limit"] = max(1, int(payload.get("limit") or DEFAULT_LIMIT))
    payload["segment"] = max(1, int(payload.get("segment") or 1))
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def init(
    repo_root: Path | str,
    *,
    limit: int = DEFAULT_LIMIT,
    session_id: str = "",
    force: bool = False,
) -> Path:
    path = budget_path(repo_root)
    if path.is_file() and not force:
        data = load(repo_root)
        if limit and limit != data.get("limit"):
            data["limit"] = max(1, int(limit))
        if session_id:
            data["session_id"] = session_id.strip()
        return _write(repo_root, data)
    return _write(repo_root, _empty(limit=limit, session_id=session_id))


def set_limit(repo_root: Path | str, limit: int) -> Path:
    data = load(repo_root) if budget_path(repo_root).is_file() else _empty()
    data["limit"] = max(1, int(limit))
    return _write(repo_root, data)


def reset(repo_root: Path | str) -> Path:
    data = load(repo_root) if budget_path(repo_root).is_file() else _empty()
    data["count"] = 0
    data["last_tool"] = ""
    # keep segment + limit
    return _write(repo_root, data)


def continue_segment(repo_root: Path | str) -> Path:
    """Cascade continue: new segment, counter back to 0, same limit."""
    data = load(repo_root) if budget_path(repo_root).is_file() else _empty()
    data["segment"] = int(data.get("segment") or 1) + 1
    data["count"] = 0
    data["last_tool"] = ""
    return _write(repo_root, data)


def assess(count: int, limit: int) -> dict[str, Any]:
    limit = max(1, int(limit))
    count = max(0, int(count))
    remaining = max(0, limit - count)
    over = count >= limit
    soft = (not over) and count >= int(limit * SOFT_RATIO)
    if over:
        level = "over"
        warn_line = (
            f"TOOL BUDGET soft: {count}/{limit} tool calls this segment. "
            "Soft stop only (no hard block). Summarize progress, ask user, or "
            "`$tool-budget` continue for a new segment."
        )
    elif soft:
        level = "soft"
        warn_line = (
            f"TOOL BUDGET soft warn: {count}/{limit} tool calls "
            f"({remaining} left). Prefer fewer tools; plan then act."
        )
    else:
        level = "ok"
        warn_line = ""
    return {
        "count": count,
        "limit": limit,
        "remaining": remaining,
        "over": over,
        "level": level,
        "warn_line": warn_line,
    }


def status(repo_root: Path | str) -> dict[str, Any]:
    data = load(repo_root)
    base = assess(int(data.get("count") or 0), int(data.get("limit") or DEFAULT_LIMIT))
    base["segment"] = int(data.get("segment") or 1)
    base["session_id"] = str(data.get("session_id") or "")
    base["last_tool"] = str(data.get("last_tool") or "")
    base["updated"] = str(data.get("updated") or "")
    base["path"] = str(budget_path(repo_root))
    return base


def increment(
    repo_root: Path | str,
    *,
    tool_name: str = "",
    session_id: str = "",
) -> dict[str, Any]:
    if not budget_path(repo_root).is_file():
        init(repo_root)
    data = load(repo_root)
    data["count"] = int(data.get("count") or 0) + 1
    if tool_name:
        data["last_tool"] = str(tool_name)[:80]
    if session_id:
        data["session_id"] = session_id.strip()
    _write(repo_root, data)
    return status(repo_root)


def _response_text(tool_response: Any) -> str:
    if tool_response is None:
        return ""
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        parts: list[str] = []
        for key in ("output", "stdout", "stderr", "message", "content"):
            val = tool_response.get(key)
            if isinstance(val, str):
                parts.append(val)
        if not parts:
            try:
                parts.append(json.dumps(tool_response)[:2000])
            except (TypeError, ValueError):
                parts.append(str(tool_response)[:2000])
        return "\n".join(parts)
    return str(tool_response)[:2000]


def _extract_exit_code(tool_response: Any, text: str) -> int | None:
    if isinstance(tool_response, dict):
        for key in ("exit_code", "returncode", "exitCode", "status_code", "status"):
            if key not in tool_response:
                continue
            try:
                return int(tool_response[key])
            except (TypeError, ValueError):
                continue
    match = _EXIT_CODE_RE.search(text or "")
    if match:
        return int(match.group(1))
    return None


def is_clean_post_tool(payload: dict[str, Any]) -> bool:
    """True when PostToolUse looks successful enough to count."""
    tool_response = payload.get("tool_response")
    text = _response_text(tool_response)
    lower = text.lower()
    exit_code = _extract_exit_code(tool_response, text)
    if exit_code is not None and exit_code != 0:
        return False
    if any(token in lower for token in _STRONG_FAIL):
        # allow "failed" only when exit unknown and strong — treat dirty
        if exit_code is None:
            return False
    return True


def _tracking_enabled(repo_root: Path | str) -> bool:
    path = Path(repo_root) / PREFS_PATH
    if not path.is_file():
        return True  # default on: soft track
    try:
        prefs = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    if not isinstance(prefs, dict):
        return True
    val = prefs.get("tool_budget_track", True)
    return bool(val)


def maybe_track_post_tool_use(
    repo_root: Path | str,
    payload: dict[str, Any],
) -> str:
    """Optional clean PostToolUse increment. Returns soft warn line or \"\"."""
    if not _tracking_enabled(repo_root):
        return ""
    if str(payload.get("hook_event_name") or "") not in ("", "PostToolUse"):
        # allow empty when called only from PostToolUse path
        if payload.get("hook_event_name") and payload.get("hook_event_name") != "PostToolUse":
            return ""
    if not is_clean_post_tool(payload):
        return ""
    tool_name = str(payload.get("tool_name") or "")
    session_id = str(payload.get("session_id") or "")
    st = increment(repo_root, tool_name=tool_name, session_id=session_id)
    return str(st.get("warn_line") or "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC tool-call budget (soft Cascade-style counter)."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON stdout for status / after mutations",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create or refresh counter file")
    p_init.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p_init.add_argument("--session-id", default="")
    p_init.add_argument("--force", action="store_true")

    sub.add_parser("status", help="Show count/limit/segment")

    p_set = sub.add_parser("set-limit", help="Change limit")
    p_set.add_argument("limit", type=int)

    p_inc = sub.add_parser("inc", help="Manual increment")
    p_inc.add_argument("--tool", default="")

    sub.add_parser("reset", help="Zero count (keep segment)")
    sub.add_parser("continue", help="New segment (Cascade continue)")

    args = parser.parse_args(argv)
    root = Path(args.project).expanduser().resolve()

    if args.cmd == "init":
        init(
            root,
            limit=args.limit,
            session_id=args.session_id,
            force=args.force,
        )
    elif args.cmd == "status":
        pass
    elif args.cmd == "set-limit":
        set_limit(root, args.limit)
    elif args.cmd == "inc":
        increment(root, tool_name=args.tool)
    elif args.cmd == "reset":
        reset(root)
    elif args.cmd == "continue":
        continue_segment(root)
    else:
        return 2

    st = status(root)
    if args.json:
        print(json.dumps(st))
    else:
        print(
            f"tool-budget: {st['count']}/{st['limit']} "
            f"segment={st['segment']} level={st['level']}"
        )
        if st.get("warn_line"):
            print(st["warn_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
