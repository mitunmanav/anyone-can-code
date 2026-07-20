"""Durable write primitives for ACC auto-memory.

Stdlib only. Every hook, MCP tool, and doctor path uses these same
functions so there is exactly one write discipline:
- append ledgers are fsynced per line (state.append_jsonl, Task 1)
- everything else is tmp -> fsync -> os.replace (atomic on NTFS/ext4)
- concurrent hooks (Codex launches matching hooks concurrently) take a
  best-effort lockfile; losing the lock degrades, never blocks chat.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import time
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|authorization)\s*[:=]\s*\S+"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
]

LOCK_NAME = "memory.lock"
HEARTBEAT_NAME = "heartbeat.json"


def scrub(text: str) -> str:
    out = text or ""
    for pattern in SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def safe_text(text: str | None) -> str:
    """Make text safe for UTF-8 disk write (Windows lone surrogates, etc.)."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Lone surrogates crash strict utf-8 encode; replace keeps chat moving.
    return text.encode("utf-8", errors="replace").decode("utf-8")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    payload = safe_text(text)
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


@contextlib.contextmanager
def memory_lock(root: Path, timeout: float = 2.0, stale: float = 10.0):
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / LOCK_NAME
    deadline = time.monotonic() + timeout
    acquired = False
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"pid": os.getpid(), "ts": time.time()}).encode("utf-8"))
            os.close(fd)
            acquired = True
            break
        except FileExistsError:
            try:
                info = json.loads(lock_path.read_text(encoding="utf-8"))
                if time.time() - float(info.get("ts", 0)) > stale:
                    lock_path.unlink(missing_ok=True)
                    continue
            except (OSError, ValueError):
                lock_path.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                break
            time.sleep(0.05)
    try:
        yield acquired
    finally:
        if acquired:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass


def write_heartbeat(memory_root: Path) -> None:
    atomic_write_text(memory_root / HEARTBEAT_NAME, json.dumps({"ts": time.time()}))


def heartbeat_age_seconds(memory_root: Path) -> float | None:
    path = memory_root / HEARTBEAT_NAME
    if not path.exists():
        return None
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
        return max(0.0, time.time() - float(info["ts"]))
    except (OSError, ValueError, KeyError):
        return None
