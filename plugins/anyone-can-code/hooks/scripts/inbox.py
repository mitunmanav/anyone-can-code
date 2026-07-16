"""Idea dump inbox: record every item from a multi-item prompt, dedupe repeats."""

from __future__ import annotations

import re
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state

ITEM_LINE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.{3,200})$")
STOPWORDS = {"a", "an", "the", "please", "add", "make", "with", "for", "to", "as", "of"}
OVERLAP_THRESHOLD = 0.6
CONTEXT_MAX = 200


def inbox_path(repo_root: Path) -> Path:
    return state.ensure_project_layout(repo_root)["state"].parent / "inbox.md"


def _normalize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def _is_duplicate(candidate: str, existing: list[str]) -> int:
    cand = _normalize(candidate)
    if not cand:
        return 0
    for idx, line in enumerate(existing, start=1):
        prev = _normalize(line)
        if not prev:
            continue
        overlap = len(cand & prev) / len(cand | prev)
        if overlap >= OVERLAP_THRESHOLD:
            return idx
    return 0


def extract_items(prompt: str) -> list[str]:
    items = []
    for line in prompt.splitlines():
        match = ITEM_LINE.match(line)
        if match:
            items.append(match.group(1).strip())
    return items if len(items) >= 2 or (items and "inbox" in prompt.lower()) else []


def read_items(repo_root: Path) -> list[str]:
    path = inbox_path(repo_root)
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- \[.\] (.+)$", line)
        if match:
            items.append(match.group(1))
    return items


def process_prompt(prompt: str, repo_root: Path) -> dict:
    """Record dump items; return counts + caveman context ('' when not a dump)."""
    candidates = extract_items(prompt)
    if not candidates:
        return {"new": 0, "total": len(read_items(repo_root)), "context": ""}

    existing = read_items(repo_root)
    added: list[str] = []
    dupes: list[int] = []
    for item in candidates:
        hit = _is_duplicate(item, existing + added)
        if hit:
            dupes.append(hit)
        else:
            added.append(item)

    if added:
        path = inbox_path(repo_root)
        with path.open("a", encoding="utf-8") as f:
            if not existing:
                f.write("# Inbox\n\n")
            for item in added:
                f.write(f"- [ ] {item}\n")

    total = len(existing) + len(added)
    parts = []
    if added:
        parts.append(f"Inbox: got {len(added)} new. {total} total.")
    if dupes:
        parts.append(f"Already have {len(dupes)} of those (#{', #'.join(str(d) for d in sorted(set(dupes)))}).")
    if added:
        parts.append("Do #1 now or keep dumping?")
    context = " ".join(parts)[:CONTEXT_MAX]
    return {"new": len(added), "total": total, "context": context}
