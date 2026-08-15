#!/usr/bin/env python3
"""Short resume card from LAST portable handoff + progress-ledger.

Explicit `$resume` helper. Stdlib only. Does not create files.
Does not replace native Codex resume (codex resume / thread/resume).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

HANDOFF_REL = Path(".codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md")
LEDGER_REL = Path(".codex/anyone-can-code/state/progress-ledger.md")

CARD_MAX_CHARS = 900
MAX_FIELD = 160
MAX_DONE_SHOW = 3
MAX_OPEN_SHOW = 3

_SECRET_PATTERNS = [
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|authorization)\s*[:=]\s*['\"]?[^\s'\"]{8,}"
    ),
    re.compile(
        r"(?i)\b(sk-[a-z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|xox[baprs]-[a-zA-Z0-9-]{20,})\b"
    ),
    re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*"),
]


def redact(text: str) -> str:
    out = str(text or "")
    for pattern in _SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def _clip(text: Any, n: int = MAX_FIELD) -> str:
    raw = redact(re.sub(r"\s+", " ", str(text or "").strip()))
    if len(raw) <= n:
        return raw
    return raw[: max(0, n - 3)].rstrip() + "..."


def handoff_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / HANDOFF_REL


def ledger_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / LEDGER_REL


def _section_body(text: str, heading: str) -> str:
    """Return lines under `## heading` until next ## or end."""
    pattern = re.compile(
        rf"(?im)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)",
        re.S,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip()


def _bullet_body(line: str) -> str:
    s = line.strip()
    if s.startswith("- [x]") or s.startswith("- [X]"):
        return s[5:].strip()
    if s.startswith("- [ ]"):
        return s[5:].strip()
    if s.startswith("- "):
        return s[2:].strip()
    return s


def load_handoff(repo_root: Path | str) -> dict[str, Any]:
    """Parse PORTABLE_HANDOFF.md (LAST handoff). Empty if missing."""
    path = handoff_path(repo_root)
    data: dict[str, Any] = {
        "present": False,
        "path": HANDOFF_REL.as_posix(),
        "goal": "",
        "next": "",
        "task": "",
        "session_id": "",
    }
    if not path.is_file():
        return data
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return data
    data["present"] = True
    data["goal"] = _clip(_section_body(text, "Goal"), 200)
    data["next"] = _clip(_section_body(text, "Next step"), 200)
    state_body = _section_body(text, "State")
    for line in state_body.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("- active_task:"):
            data["task"] = _clip(stripped.split(":", 1)[1], 160)
            break
    sid_match = re.search(r"(?im)^\s*-\s*session_id:\s*(\S+)", text)
    if sid_match:
        sid = sid_match.group(1).strip()
        if sid.lower() not in {"none", "n/a", "-"}:
            data["session_id"] = _clip(sid, 80)
    return data


def load_ledger(repo_root: Path | str) -> dict[str, Any]:
    """Parse progress-ledger.md if present. Soft — no create."""
    path = ledger_path(repo_root)
    data: dict[str, Any] = {
        "present": False,
        "path": LEDGER_REL.as_posix(),
        "where": "",
        "next": "",
        "done": [],
        "open": [],
    }
    if not path.is_file():
        return data
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return data
    data["present"] = True
    section = ""
    where_lines: list[str] = []
    next_lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip().upper()
            continue
        if not stripped or stripped.startswith("# "):
            continue
        if section == "WHERE":
            where_lines.append(stripped)
        elif section == "NEXT":
            next_lines.append(stripped)
        elif section == "DONE":
            body = _bullet_body(stripped)
            if body and body.lower() not in {"(none yet)", "(none)"}:
                data["done"].append(_clip(body, 120))
        elif section == "OPEN":
            body = _bullet_body(stripped)
            if body and body.lower() not in {"(none yet)", "(none)"}:
                data["open"].append(_clip(body, 120))
    data["where"] = _clip(" ".join(where_lines), 200) if where_lines else ""
    data["next"] = _clip(" ".join(next_lines), 200) if next_lines else ""
    return data


def _usable(value: str) -> bool:
    v = (value or "").strip().lower()
    return bool(v) and v not in {"not set", "(none)", "n/a", "none"}


def build_card(repo_root: Path | str) -> str:
    """Short resume card. Handoff + ledger if present. Hard size cap."""
    root = Path(repo_root)
    handoff = load_handoff(root)
    ledger = load_ledger(root)

    # Ledger WHERE/NEXT win when set; else handoff goal/next.
    where = ""
    if ledger["present"] and _usable(ledger.get("where", "")):
        where = str(ledger["where"])
    elif handoff["present"] and _usable(handoff.get("goal", "")):
        where = str(handoff["goal"])
    elif handoff["present"] and _usable(handoff.get("task", "")):
        where = str(handoff["task"])

    nxt = ""
    if ledger["present"] and _usable(ledger.get("next", "")):
        nxt = str(ledger["next"])
    elif handoff["present"] and _usable(handoff.get("next", "")):
        nxt = str(handoff["next"])

    done = list(ledger.get("done") or [])[-MAX_DONE_SHOW:] if ledger["present"] else []
    open_items = (
        list(ledger.get("open") or [])[-MAX_OPEN_SHOW:] if ledger["present"] else []
    )

    handoff_status = "present" if handoff["present"] else "missing"
    ledger_status = "present" if ledger["present"] else "missing"

    lines = [
        "# Resume card",
        f"WHERE: {_clip(where, 160) if where else '(not set — open handoff/ledger or $status)'}",
        f"NEXT: {_clip(nxt, 160) if nxt else '(not set)'}",
    ]
    if done:
        lines.append("DONE: " + "; ".join(_clip(d, 80) for d in done))
    elif ledger["present"]:
        lines.append("DONE: (none)")
    if open_items:
        lines.append("OPEN: " + "; ".join(_clip(o, 80) for o in open_items))
    elif ledger["present"]:
        lines.append("OPEN: (none)")

    lines.append(f"HANDOFF: {handoff_status}  path={HANDOFF_REL.as_posix()}")
    lines.append(f"LEDGER: {ledger_status}  path={LEDGER_REL.as_posix()}")

    sid = handoff.get("session_id") or ""
    if sid:
        lines.append(
            f"Native: still on Codex? `codex resume {sid}` or `thread/resume`; "
            "else read handoff file."
        )
    else:
        lines.append(
            "Native: still on Codex? `codex resume --last` / `thread/resume`; "
            "else read handoff file. Cross-tool: PORTABLE_HANDOFF only."
        )
    lines.append(
        "Rules: no invent. Light recovery first. Verify before done. "
        "Hooks optional — disk truth wins after compact."
    )
    card = "\n".join(lines) + "\n"
    if len(card) > CARD_MAX_CHARS:
        card = card[: max(0, CARD_MAX_CHARS - 4)].rstrip() + "...\n"
    return card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC short resume card (handoff + progress-ledger)"
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd)",
    )
    args = parser.parse_args(argv)
    root = Path(args.project).resolve()
    print(build_card(root), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
