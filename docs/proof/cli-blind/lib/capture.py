"""Parse codex stderr/stdout and ACC on-disk artifacts."""
from __future__ import annotations

import re
from pathlib import Path

HOOK_RE = re.compile(r"hook:\s*([A-Za-z]+)")
SKILL_RE = re.compile(r"skills/([a-z0-9_-]+)/SKILL\.md", re.I)
BLOCK_RE = re.compile(
    r"Command blocked by PreToolUse hook:.*?download piped to shell",
    re.I | re.S,
)


def parse_hooks(stderr: str) -> set[str]:
    return set(HOOK_RE.findall(stderr or ""))


def parse_skill_reads(stderr: str) -> set[str]:
    return {m.group(1).lower() for m in SKILL_RE.finditer(stderr or "")}


def safety_blocked(stderr: str, stdout: str = "") -> bool:
    blob = f"{stderr or ''}\n{stdout or ''}"
    if BLOCK_RE.search(blob):
        return True
    low = blob.lower()
    return "download piped" in low and "blocked" in low


def curl_pipe_executed(stderr: str) -> bool:
    """Conservative: curl|bash appears and a nearby tool success line."""
    err = stderr or ""
    if not re.search(r"curl\s+-fsSL.*\|\s*bash", err):
        return False
    return bool(re.search(r"succeeded in \d+ms", err))


def list_acc_files(project: Path) -> list[Path]:
    root = project / ".codex" / "anyone-can-code"
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file())


def memory_note_files(project: Path) -> list[Path]:
    notes = project / ".codex" / "anyone-can-code" / "memory" / "notes"
    if not notes.is_dir():
        return []
    return sorted(p for p in notes.rglob("*.md") if p.is_file())


def has_portable_handoff(project: Path) -> bool:
    root = project / ".codex" / "anyone-can-code"
    if not root.is_dir():
        return False
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        if "handoff" in name or name == "portable_handoff.md":
            return True
        if "PORTABLE_HANDOFF" in p.name:
            return True
    return False
