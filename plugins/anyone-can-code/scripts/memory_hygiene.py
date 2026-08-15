#!/usr/bin/env python3
"""ACC wiki memory hygiene — age notes, flag secrets, never store full chat.

Product memory = portable Markdown under:
  .codex/anyone-can-code/memory/notes/

NOT Codex native ~/.codex/memories/ or /memories.

Report-only by default (scan / validate). Skill $memory-hygiene shows the
report and waits for user YES before any archive/scrub write.

Grounding:
- GitHub Copilot Memory: unused facts expire after 28 days; citations for
  repo facts (WEB docs.github.com/en/copilot/concepts/agents/copilot-memory).
- Codex Memories docs: redacts secrets from generated memory fields; do not
  store secrets; local memories are a separate product surface ACC keeps OFF.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# Align with Copilot Memory unused retention (28 days).
DEFAULT_STALE_DAYS = 28
# Short durable notes only — full transcripts are not wiki facts.
MAX_STORE_CHARS = 2_000
# Multi-turn chat dump heuristics.
MIN_TURN_MARKERS_FOR_CHAT = 8
CHAT_TURN_RE = re.compile(
    r"(?im)^\s*(user|assistant|human|system|chatgpt|codex)\s*[:\-]"
)
# Secret patterns — same family as memory_core / MCP scrub.
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "api_key",
        re.compile(
            r"(?i)(api[_-]?key|token|secret|password|passwd|authorization)\s*[:=]\s*\S+"
        ),
    ),
    ("openai_sk", re.compile(r"sk-[A-Za-z0-9_\-]{16,}")),
    ("bearer", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}")),
    ("github_pat", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
]


def memory_root_for(project_root: Path) -> Path:
    return Path(project_root) / ".codex" / "anyone-can-code" / "memory"


def notes_root(project_root: Path) -> Path:
    return memory_root_for(project_root) / "notes"


def iter_note_paths(project_root: Path) -> list[Path]:
    root = notes_root(project_root)
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def note_rel(path: Path, project_root: Path) -> str:
    mem = memory_root_for(project_root)
    try:
        return str(path.relative_to(mem)).replace("\\", "/")
    except ValueError:
        try:
            return str(path.relative_to(project_root)).replace("\\", "/")
        except ValueError:
            return path.name


def note_age_days(path: Path, now: float | None = None) -> float:
    now = time.time() if now is None else now
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return 0.0
    return max(0.0, (now - mtime) / 86400.0)


def detect_secret_kinds(text: str) -> list[str]:
    kinds: list[str] = []
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(text or ""):
            kinds.append(name)
    return kinds


def scrub_text(text: str) -> str:
    out = text or ""
    for _name, pattern in SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def looks_like_full_chat(text: str) -> bool:
    """True when body looks like a multi-turn chat dump, not a short note."""
    body = text or ""
    if len(body) > MAX_STORE_CHARS:
        # Long alone is not always chat — still flag as full_chat when huge.
        if len(body) > MAX_STORE_CHARS * 2:
            return True
    markers = CHAT_TURN_RE.findall(body)
    if len(markers) >= MIN_TURN_MARKERS_FOR_CHAT:
        return True
    # Dense alternating User:/Assistant: blocks
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    turn_lines = sum(1 for ln in lines if CHAT_TURN_RE.match(ln))
    if turn_lines >= MIN_TURN_MARKERS_FOR_CHAT:
        return True
    return False


def validate_store_candidate(text: str) -> dict[str, Any]:
    """Gate for anything about to become a durable wiki note.

    Never store full chat. Never store secret-bearing text as-is.
    """
    reasons: list[str] = []
    body = text or ""
    if looks_like_full_chat(body):
        reasons.append("full_chat")
    if len(body) > MAX_STORE_CHARS and "full_chat" not in reasons:
        # Over cap without chat markers: still refuse bulk dump.
        reasons.append("too_long")
    if detect_secret_kinds(body):
        reasons.append("secret")
    return {
        "ok": not reasons,
        "reasons": reasons,
        "max_chars": MAX_STORE_CHARS,
        "char_count": len(body),
    }


def scan_memory(
    project_root: Path,
    *,
    stale_days: int = DEFAULT_STALE_DAYS,
    now: float | None = None,
) -> dict[str, Any]:
    """Read-only hygiene report for ACC wiki notes. Never writes."""
    project_root = Path(project_root)
    now = time.time() if now is None else now
    mem = memory_root_for(project_root)
    paths = iter_note_paths(project_root)
    stale: list[dict[str, Any]] = []
    secret_hits: list[dict[str, Any]] = []
    full_chat_hits: list[dict[str, Any]] = []

    for path in paths:
        rel = note_rel(path, project_root)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        age = note_age_days(path, now=now)
        if age >= float(stale_days):
            stale.append(
                {
                    "rel": rel,
                    "age_days": round(age, 1),
                    "action": "archive_or_refresh",
                }
            )
        kinds = detect_secret_kinds(text)
        if kinds:
            secret_hits.append(
                {
                    "rel": rel,
                    "kinds": kinds,
                    "action": "scrub_or_revoke",
                    # Never include raw secret values in the report.
                    "preview": scrub_text(text)[:120].replace("\n", " "),
                }
            )
        if looks_like_full_chat(text):
            full_chat_hits.append(
                {
                    "rel": rel,
                    "char_count": len(text),
                    "action": "replace_with_short_summary",
                }
            )

    return {
        "product": "acc-wiki",
        "not_product": "codex-native-memories",
        "memory_root": str(mem),
        "note_count": len(paths),
        "stale_days": int(stale_days),
        "stale": stale,
        "secret_hits": secret_hits,
        "full_chat_hits": full_chat_hits,
        "ok": not secret_hits and not full_chat_hits,
        "summary": _summary_line(
            len(paths), stale, secret_hits, full_chat_hits, stale_days
        ),
    }


def _summary_line(
    note_count: int,
    stale: list,
    secrets: list,
    chats: list,
    stale_days: int,
) -> str:
    parts = [
        f"{note_count} notes",
        f"{len(stale)} stale(>={stale_days}d)",
        f"{len(secrets)} secret-flags",
        f"{len(chats)} full-chat-flags",
    ]
    return "ACC wiki hygiene: " + ", ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ACC wiki memory hygiene (report only). "
            "Ages notes, flags secrets, flags full-chat dumps. "
            "Never writes. Never uses Codex /memories."
        )
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=DEFAULT_STALE_DAYS,
        help=f"Age threshold in days (default {DEFAULT_STALE_DAYS}, Copilot-style)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON report",
    )
    parser.add_argument(
        "--validate-text",
        default=None,
        help="Validate a candidate store string (stdin if '-')",
    )
    args = parser.parse_args(argv)

    if args.validate_text is not None:
        if args.validate_text == "-":
            text = sys.stdin.read()
        else:
            text = args.validate_text
        result = validate_store_candidate(text)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("OK" if result["ok"] else "REJECT: " + ",".join(result["reasons"]))
        return 0 if result["ok"] else 2

    report = scan_memory(
        Path(args.project_root).resolve(),
        stale_days=max(1, int(args.stale_days)),
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(report["summary"])
        for item in report["stale"][:10]:
            print(f"  stale: {item['rel']} ({item['age_days']}d) → {item['action']}")
        for item in report["secret_hits"][:10]:
            print(f"  secret: {item['rel']} kinds={item['kinds']} → {item['action']}")
        for item in report["full_chat_hits"][:10]:
            print(
                f"  full-chat: {item['rel']} ({item['char_count']} chars) → {item['action']}"
            )
        if report["ok"] and not report["stale"]:
            print("  clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
