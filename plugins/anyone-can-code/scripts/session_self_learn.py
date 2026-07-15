#!/usr/bin/env python3
"""Free self-learning — scan local Codex sessions, zero model tokens.

Item 8: CHEAP. Reads ~/.codex/sessions rollout JSONL (same disk truth as
codeburn / rate_limit_guard). Pulls plain candidate lessons from failures
and user corrections. Does NOT call AI.

Default: report only. Optional --write stores project lessons via MCP when
project_root is given.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


# Signals that mean "learn this, don't repeat"
_FAIL_MARKERS = (
    "error",
    "failed",
    "traceback",
    "exception",
    "exit code 1",
    "exit status 1",
    "command not found",
    "permission denied",
)
_USER_CORRECTION = (
    "you were wrong",
    "that is wrong",
    "don't do that",
    "do not",
    "never ",
    "always use",
    "stop doing",
)

MAX_LESSONS = 12
MAX_LINE = 160


def session_dirs() -> list[Path]:
    dirs: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        dirs.append(Path(codex_home) / "sessions")
    dirs.append(Path.home() / ".codex" / "sessions")
    seen: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        k = str(d)
        if k not in seen:
            seen.add(k)
            out.append(d)
    return out


def list_recent_rollouts(roots: list[Path] | None = None, limit: int = 20) -> list[Path]:
    roots = roots if roots is not None else session_dirs()
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            found.extend(root.rglob("rollout-*.jsonl"))
        except OSError:
            continue
    found.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return found[:limit]


def _trim(text: str, limit: int = MAX_LINE) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _extract_from_line(line: str) -> list[str]:
    """Return candidate lesson strings from one JSONL line."""
    line = line.strip()
    if not line:
        return []
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return []
    out: list[str] = []
    etype = entry.get("type")
    payload = entry.get("payload") or {}

    # User messages that correct the agent
    if etype in {"response_item", "event_msg"}:
        # agent messages with failure talk
        text_bits: list[str] = []
        if isinstance(payload, dict):
            if payload.get("type") == "user_message" or payload.get("role") == "user":
                content = payload.get("content") or payload.get("message") or ""
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            text_bits.append(str(part.get("text") or ""))
                        else:
                            text_bits.append(str(part))
                else:
                    text_bits.append(str(content))
            msg = payload.get("message")
            if isinstance(msg, str):
                text_bits.append(msg)
            # tool / command failures in text
            for key in ("text", "output", "command"):
                val = payload.get(key)
                if isinstance(val, str):
                    text_bits.append(val)

        blob = " ".join(text_bits).strip()
        if not blob:
            return []
        low = blob.lower()
        if any(m in low for m in _USER_CORRECTION):
            out.append(_trim(f"User correction: {blob}"))
        elif any(m in low for m in _FAIL_MARKERS) and len(blob) < 400:
            # short failure lines only — avoid dumping huge logs
            out.append(_trim(f"Failure signal: {blob}"))
    return out


def mine_sessions(
    roots: list[Path] | None = None,
    *,
    max_files: int = 15,
    max_lines_per_file: int = 3000,
) -> dict[str, Any]:
    """Mine recent sessions for candidate lessons. Zero AI tokens."""
    counter: Counter[str] = Counter()
    files_scanned = 0
    for path in list_recent_rollouts(roots, limit=max_files):
        files_scanned += 1
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines[-max_lines_per_file:]:
            for lesson in _extract_from_line(line):
                # collapse near-duplicates by lower key
                counter[lesson] += 1

    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:MAX_LESSONS]
    lessons = [
        {"summary": summary, "hits": hits, "kind": "lesson"}
        for summary, hits in ranked
    ]
    return {
        "files_scanned": files_scanned,
        "lessons": lessons,
        "count": len(lessons),
        "token_cost": 0,
        "message": (
            f"Free self-learn: {len(lessons)} candidate lesson(s) from "
            f"{files_scanned} session file(s). Zero AI tokens."
        ),
    }


def write_lessons_to_project(project_root: Path, lessons: list[dict[str, Any]]) -> dict[str, Any]:
    """Optional: store top lessons as project memory notes (stdlib path write)."""
    notes_dir = (
        Path(project_root)
        / ".codex"
        / "anyone-can-code"
        / "memory"
        / "notes"
        / "project"
    )
    notes_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for i, item in enumerate(lessons[:8]):
        summary = str(item.get("summary") or "").strip()
        if not summary:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", summary.lower())[:40].strip("-") or f"lesson-{i}"
        path = notes_dir / f"self-learn-{slug}.md"
        if path.exists():
            continue
        body = (
            "---\n"
            f'id: "self-learn-{slug}"\n'
            'kind: "lesson"\n'
            'scope: "project"\n'
            'status: "active"\n'
            f"reinforcement_count: {int(item.get('hits') or 1)}\n"
            "---\n\n"
            "# Self-learn lesson\n\n"
            "## Summary\n\n"
            f"{summary}\n\n"
            "## Evidence\n\n"
            "Mined free from local Codex session files (no AI).\n"
        )
        path.write_text(body, encoding="utf-8")
        written += 1
    return {"written": written, "dir": str(notes_dir)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Free self-learning from Codex sessions")
    parser.add_argument("--sessions-root", type=str, default="", help="Override sessions root")
    parser.add_argument("--project-root", type=str, default="", help="Project for optional --write")
    parser.add_argument("--write", action="store_true", help="Write lessons into project memory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    roots = [Path(args.sessions_root)] if args.sessions_root else None
    result = mine_sessions(roots)
    if args.write:
        if not args.project_root:
            print("Need --project-root with --write", file=sys.stderr)
            return 2
        result["write"] = write_lessons_to_project(Path(args.project_root), result["lessons"])
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["message"])
        for item in result["lessons"]:
            print(f"- ({item['hits']}x) {item['summary']}")
        if args.write and "write" in result:
            print(f"Wrote {result['write']['written']} new note(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
