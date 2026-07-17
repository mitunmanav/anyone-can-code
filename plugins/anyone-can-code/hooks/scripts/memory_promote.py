"""Deterministic promote rules: user wants, decisions, corrections -> durable notes.

No AI, no agent goodwill. Rules run inside hook processes. Misses are
acceptable (the prompt log still has the raw line); false saves are cheap
(notes are revocable). Note format matches load_session.recall_memory_notes.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_core
import state

MAX_PROMOTES_PER_CALL = 3
EXCERPT_MAX_CHARS = 200

NEGATIVE_RE = re.compile(r"(?i)\b(never ?mind|don'?t worry|no problem|forget it)\b")

PROMPT_RULES = [
    ("want", re.compile(
        r"(?i)\b(i want|please always|always use|always ask|never use|never |don'?t ever|"
        r"do not ever|i prefer|remember that|from now on)\b")),
    ("correction", re.compile(
        r"(?i)(\bno[,.]|that'?s wrong|you'?re wrong|\bi said\b|stop doing|not what i asked)")),
    ("decision", re.compile(
        r"(?i)\b(go with|use .{1,40} instead|switch(ing)? to|decided|final answer|yes,? do)\b")),
]

STOP_RULES = [
    ("decision", re.compile(
        r"(?i)\b(decided|going with|we'?ll use|locked in|switch(ing)? to|chose)\b")),
]

_SENTENCE_SPLIT = re.compile(r"[.\n!?]+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text or "") if s.strip()]


def detect_promotes(text: str, source: str) -> list[dict]:
    clean = memory_core.scrub(text or "")
    if NEGATIVE_RE.search(clean):
        return []
    rules = PROMPT_RULES if source == "prompt" else STOP_RULES
    hits: list[dict] = []
    seen: set[str] = set()
    for sentence in _sentences(clean):
        for kind, pattern in rules:
            if pattern.search(sentence):
                excerpt = sentence[:EXCERPT_MAX_CHARS]
                if excerpt.lower() in seen:
                    continue
                seen.add(excerpt.lower())
                hits.append({"kind": kind, "excerpt": excerpt})
                break
        if len(hits) >= MAX_PROMOTES_PER_CALL:
            break
    return hits


def _content_hash(kind: str, excerpt: str) -> str:
    normal = re.sub(r"\s+", " ", excerpt.lower().strip())
    return hashlib.sha256(f"{kind}:{normal}".encode("utf-8")).hexdigest()[:16]


def write_promote_note(repo_root: Path, kind: str, excerpt: str) -> str:
    layout = state.ensure_project_layout(repo_root)
    notes_dir: Path = layout["memory"] / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    excerpt = memory_core.scrub(excerpt.strip())[:EXCERPT_MAX_CHARS]
    if not excerpt:
        return ""
    digest = _content_hash(kind, excerpt)
    registry_path = notes_dir / ".hashes.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        registry = {}

    with memory_core.memory_lock(layout["memory"]):
        if digest in registry:
            name = registry[digest]
            note_path = notes_dir / name
            if note_path.exists():
                text = note_path.read_text(encoding="utf-8")
                match = re.search(r"reinforcement_count:\s*(\d+)", text)
                count = int(match.group(1)) + 1 if match else 2
                text = re.sub(r"reinforcement_count:\s*\d+",
                              f"reinforcement_count: {count}", text, count=1)
                memory_core.atomic_write_text(note_path, text)
                return name
        name = f"auto-{kind}-{digest}.md"
        body = "\n".join([
            "---",
            f'kind: "{kind}"',
            'status: "active"',
            "reinforcement_count: 1",
            f'created: "{state.utc_now()}"',
            f'content_hash: "{digest}"',
            'source: "hook:promote"',
            "---",
            "",
            "## Summary",
            excerpt,
            "",
        ])
        memory_core.atomic_write_text(notes_dir / name, body)
        registry[digest] = name
        memory_core.atomic_write_text(registry_path, json.dumps(registry, indent=0))
        (layout["memory"] / "memory.sqlite").unlink(missing_ok=True)  # lazy reindex on next search
    return name
