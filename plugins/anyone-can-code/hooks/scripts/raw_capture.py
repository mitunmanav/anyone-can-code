"""Append-only raw turn capture into project memory/raw/.

ADD-ONLY layer: user prompts + assistant replies land as separate roles.
Redact secrets before write. Never inject full chat into SessionStart.

Codex docs (hooks):
- UserPromptSubmit stdin: prompt, turn_id, session_id
- Stop stdin: last_assistant_message, turn_id, stop_hook_active
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_core
import state

SCHEMA_VERSION = 1
TURNS_FILE = "turns.jsonl"
# Bound single turn size so raw stays mineable, not a transcript dump.
MAX_TEXT_CHARS = 32000
SOURCE_USER = "hook:UserPromptSubmit"
SOURCE_ASSISTANT = "hook:Stop"


def raw_turns_path(repo_root: Path) -> Path:
    layout = state.ensure_project_layout(repo_root)
    return layout["memory_raw"] / TURNS_FILE


def _trim_text(text: str) -> str:
    text = memory_core.safe_text(text or "").strip()
    if len(text) <= MAX_TEXT_CHARS:
        return text
    return text[:MAX_TEXT_CHARS].rstrip() + "..."


def content_hash(role: str, text: str) -> str:
    normal = re.sub(r"\s+", " ", (text or "").lower().strip())
    return hashlib.sha256(f"{role}|{normal}".encode("utf-8")).hexdigest()[:16]


def build_raw_entry(
    *,
    role: str,
    text: str,
    payload: dict | None = None,
    source: str = "",
) -> dict | None:
    """Build one redacted raw turn row. Returns None if empty after scrub."""
    if role not in {"user", "assistant"}:
        raise ValueError(f"invalid role: {role}")
    payload = payload or {}
    cleaned = _trim_text(text)
    if not cleaned:
        return None
    scrubbed = memory_core.scrub(cleaned)
    secret_redacted = scrubbed != cleaned
    entry = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": state.utc_now(),
        "role": role,
        "text": scrubbed,
        "content_hash": content_hash(role, scrubbed),
        "secret_redacted": secret_redacted,
        "source": source
        or (SOURCE_USER if role == "user" else SOURCE_ASSISTANT),
        "session_id": str(payload.get("session_id") or ""),
        "turn_id": str(payload.get("turn_id") or ""),
    }
    return entry


def append_raw_turn(repo_root: Path, entry: dict) -> Path | None:
    """Append one turn to memory/raw/turns.jsonl. Immutable append (no rotate)."""
    if not entry or not entry.get("text"):
        return None
    path = raw_turns_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    # Best-effort lock so concurrent UserPromptSubmit/Stop don't interleave badly.
    with memory_core.memory_lock(path.parent, timeout=1.0):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass
    return path


def capture_user_prompt(repo_root: Path, payload: dict) -> Path | None:
    """UserPromptSubmit → raw user turn."""
    entry = build_raw_entry(
        role="user",
        text=str(payload.get("prompt") or ""),
        payload=payload,
        source=SOURCE_USER,
    )
    if not entry:
        return None
    return append_raw_turn(repo_root, entry)


def capture_assistant_turn(repo_root: Path, payload: dict) -> Path | None:
    """Stop → raw assistant turn from last_assistant_message."""
    entry = build_raw_entry(
        role="assistant",
        text=str(payload.get("last_assistant_message") or ""),
        payload=payload,
        source=SOURCE_ASSISTANT,
    )
    if not entry:
        return None
    return append_raw_turn(repo_root, entry)


def read_raw_turns(repo_root: Path, limit: int | None = None) -> list[dict]:
    """Read raw turns (oldest first). limit=None → all; else last N."""
    path = raw_turns_path(repo_root)
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    if limit is not None and limit > 0:
        lines = lines[-limit:]
    for line in lines:
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
