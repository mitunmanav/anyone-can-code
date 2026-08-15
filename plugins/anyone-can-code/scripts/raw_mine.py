#!/usr/bin/env python3
"""Pure-Python rules that mine prefs/facts from memory/raw/ into notes/.

Scripts own mining. Model is not required. ADD-ONLY on top of existing
notes/wiki/learn/two-drawer product.

Usage (offline or from Stop):
  python3 raw_mine.py --repo-root /path/to/project
  python3 raw_mine.py --repo-root /path --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))
import memory_core  # noqa: E402
import raw_capture  # noqa: E402
import state  # noqa: E402

MAX_NOTES_PER_RUN = 5
EXCERPT_MAX = 200
CURSOR_NAME = "raw-mine-cursor.json"
SOURCE = "script:raw_mine"

# First mine rules (v1): user-role gold only. Assistant text is corpus, not primary.
# Prefer explicit preference / stack / don't-do language.
MINE_RULES: list[tuple[str, re.Pattern[str], float]] = [
    (
        "preference",
        re.compile(
            r"(?i)\b(i prefer|please always|always use|always ask|from now on|"
            r"be brief|strict caveman|talk short|i want you to always)\b"
        ),
        0.75,
    ),
    (
        "preference",
        re.compile(
            r"(?i)\b(never use|never |don'?t ever|do not ever|don'?t use)\b"
        ),
        0.7,
    ),
    (
        "decision",
        re.compile(
            r"(?i)\b(use .{1,40} for |switch(ing)? to |go with |decided |"
            r"we'?ll use |locked in )\b"
        ),
        0.65,
    ),
    (
        "lesson",
        re.compile(
            r"(?i)\b(don'?t do |do not do |never do |stop doing |must not )\b"
        ),
        0.7,
    ),
]

NEGATIVE_RE = re.compile(r"(?i)\b(never ?mind|don'?t worry|no problem|forget it)\b")
_SENTENCE_SPLIT = re.compile(r"[.\n!?]+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text or "") if s.strip()]


def detect_mine_hits(text: str, role: str = "user") -> list[dict]:
    """Return rule hits for one turn. User turns preferred; assistant optional later."""
    if role != "user":
        return []
    clean = memory_core.scrub(text or "")
    if not clean or NEGATIVE_RE.search(clean):
        return []
    hits: list[dict] = []
    seen: set[str] = set()
    for sentence in _sentences(clean):
        for kind, pattern, confidence in MINE_RULES:
            if not pattern.search(sentence):
                continue
            excerpt = sentence[:EXCERPT_MAX]
            key = excerpt.lower()
            if key in seen:
                continue
            seen.add(key)
            hits.append(
                {
                    "kind": kind,
                    "excerpt": excerpt,
                    "confidence": confidence,
                }
            )
            break
        if len(hits) >= MAX_NOTES_PER_RUN:
            break
    return hits


def _content_hash(kind: str, excerpt: str) -> str:
    normal = re.sub(r"\s+", " ", excerpt.lower().strip())
    return hashlib.sha256(f"mine:{kind}:{normal}".encode("utf-8")).hexdigest()[:16]


def _cursor_path(repo_root: Path) -> Path:
    return state.ensure_project_layout(repo_root)["state"] / CURSOR_NAME


def load_cursor(repo_root: Path) -> int:
    path = _cursor_path(repo_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return int(data.get("lines_read", 0) or 0)
    except (OSError, ValueError, TypeError):
        return 0


def save_cursor(repo_root: Path, lines_read: int) -> None:
    path = _cursor_path(repo_root)
    memory_core.atomic_write_text(
        path,
        json.dumps(
            {"lines_read": int(lines_read), "updated_at": state.utc_now()},
            indent=0,
        )
        + "\n",
    )


def write_mined_note(
    repo_root: Path,
    *,
    kind: str,
    excerpt: str,
    confidence: float,
    raw_hash: str,
    turn_role: str,
) -> str:
    """Write or reinforce one note under memory/notes/. Pointer into raw."""
    layout = state.ensure_project_layout(repo_root)
    notes_dir: Path = layout["memory"] / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    excerpt = memory_core.scrub(excerpt.strip())[:EXCERPT_MAX]
    if not excerpt:
        return ""
    digest = _content_hash(kind, excerpt)
    registry_path = notes_dir / ".mine-hashes.json"
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
                text = re.sub(
                    r"reinforcement_count:\s*\d+",
                    f"reinforcement_count: {count}",
                    text,
                    count=1,
                )
                memory_core.atomic_write_text(note_path, text)
                return name
        name = f"mine-{kind}-{digest}.md"
        body = "\n".join(
            [
                "---",
                f'kind: "{kind}"',
                'status: "active"',
                "reinforcement_count: 1",
                f"confidence: {confidence:.2f}",
                f'created: "{state.utc_now()}"',
                f'content_hash: "{digest}"',
                f'source: "{SOURCE}"',
                f'raw_pointer: "raw/turns.jsonl#{raw_hash}"',
                f'raw_role: "{turn_role}"',
                "---",
                "",
                "## Summary",
                excerpt,
                "",
                "## Evidence",
                f"Mined from project drawer raw turn `{raw_hash}` ({turn_role}).",
                "",
            ]
        )
        memory_core.atomic_write_text(notes_dir / name, body)
        registry[digest] = name
        memory_core.atomic_write_text(
            registry_path, json.dumps(registry, indent=0) + "\n"
        )
        (layout["memory"] / "memory.sqlite").unlink(missing_ok=True)
    return name


def mine_raw(
    repo_root: Path,
    *,
    dry_run: bool = False,
    max_notes: int = MAX_NOTES_PER_RUN,
) -> dict:
    """Mine new raw turns since cursor. Returns counts + note names."""
    path = raw_capture.raw_turns_path(repo_root)
    if not path.exists():
        return {
            "ok": True,
            "mined": 0,
            "notes": [],
            "lines_read": 0,
            "skipped": "no_raw",
        }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return {"ok": False, "error": str(exc), "mined": 0, "notes": []}

    cursor = load_cursor(repo_root)
    if cursor > len(lines):
        cursor = 0  # file truncated externally — re-scan safely via hash registry

    notes: list[str] = []
    mined = 0
    for line in lines[cursor:]:
        if mined >= max_notes:
            break
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = str(row.get("role") or "")
        text = str(row.get("text") or "")
        raw_hash = str(row.get("content_hash") or "")
        for hit in detect_mine_hits(text, role=role):
            if mined >= max_notes:
                break
            if dry_run:
                notes.append(f"dry:{hit['kind']}:{hit['excerpt'][:60]}")
                mined += 1
                continue
            name = write_mined_note(
                repo_root,
                kind=hit["kind"],
                excerpt=hit["excerpt"],
                confidence=float(hit["confidence"]),
                raw_hash=raw_hash or "unknown",
                turn_role=role,
            )
            if name:
                notes.append(name)
                mined += 1

    new_cursor = len(lines)
    if not dry_run:
        save_cursor(repo_root, new_cursor)
        if mined:
            try:
                scripts = Path(__file__).resolve().parent
                if str(scripts) not in sys.path:
                    sys.path.insert(0, str(scripts))
                import wiki_memory as _wiki  # type: ignore

                mem = state.ensure_project_layout(repo_root)["memory"]
                _wiki.rebuild_human_index(mem)
                _wiki.append_log(
                    mem, "raw-mine", f"wrote {mined} note(s) from raw turns"
                )
            except Exception:
                pass

    return {
        "ok": True,
        "mined": mined,
        "notes": notes,
        "lines_read": new_cursor,
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mine ACC memory/raw into notes")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-notes", type=int, default=MAX_NOTES_PER_RUN)
    args = parser.parse_args(argv)
    result = mine_raw(
        args.repo_root.resolve(),
        dry_run=args.dry_run,
        max_notes=args.max_notes,
    )
    print(json.dumps(result))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
