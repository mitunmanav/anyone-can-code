#!/usr/bin/env python3
"""Fingerprint repeated keywords/lessons from notes or prompt-log.

Suggest only — never write wiki/learn notes or AGENTS.md. The $rule-suggest
skill shows proposals and waits for explicit user YES before any write.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPEAT_THRESHOLD = 3
MAX_SUGGESTIONS = 5
SAMPLE_MAX = 160
LESSON_MAX = 200

STOP_WORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "have",
        "has",
        "was",
        "were",
        "are",
        "you",
        "your",
        "our",
        "not",
        "but",
        "can",
        "will",
        "just",
        "into",
        "about",
        "then",
        "than",
        "when",
        "what",
        "which",
        "who",
        "how",
        "why",
        "all",
        "any",
        "out",
        "use",
        "using",
        "used",
        "please",
        "still",
        "again",
        "need",
        "want",
        "make",
        "made",
        "get",
        "got",
        "run",
        "running",
        "try",
        "trying",
        "also",
        "too",
        "very",
        "more",
        "some",
        "same",
        "like",
        "does",
        "did",
        "doing",
        "dont",
        "don",
        "its",
        "let",
        "lets",
        "should",
        "would",
        "could",
        "there",
        "here",
        "been",
        "being",
        "them",
        "they",
        "their",
        "over",
        "under",
        "after",
        "before",
        "once",
        "only",
        "onto",
        "via",
        "per",
        "each",
        "every",
        "other",
        "such",
        "than",
        "because",
        "while",
        "where",
        "code",
        "file",
        "files",
        "line",
        "lines",
        "fix",
        "fixed",
        "error",
        "errors",
        "issue",
        "issues",
        "bug",
        "bugs",
        "please",
        "thanks",
        "okay",
        "yes",
        "yeah",
        "nope",
        "true",
        "false",
        "null",
        "none",
        "todo",
        "acc",
        "codex",
        "project",
        "summary",
        "evidence",
        "links",
        "receipt",
        "source",
        "status",
        "active",
        "kind",
        "scope",
        "user",
        "shared",
    }
)


def acc_root(project_root: Path) -> Path:
    return Path(project_root) / ".codex" / "anyone-can-code"


def fingerprint(text: str) -> str:
    """Normalize text to a stable keyword fingerprint for repeat detection."""
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    keep = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
    # Stable order, de-dupe while preserving first-seen order
    seen: set[str] = set()
    ordered: list[str] = []
    for w in keep:
        if w not in seen:
            seen.add(w)
            ordered.append(w)
    return " ".join(ordered[:12])


def _trim(text: str, limit: int = SAMPLE_MAX) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _lesson_from_bullet(line: str) -> str | None:
    text = line.strip()
    if not text.startswith("-"):
        return None
    lesson = text.lstrip("-* ").strip()
    if not lesson or lesson.startswith("#"):
        return None
    return lesson[:LESSON_MAX]


def collect_source_lines(project_root: Path) -> list[tuple[str, str]]:
    """Return (source_tag, text) from memory notes and prompt-log if present."""
    root = acc_root(project_root)
    out: list[tuple[str, str]] = []

    notes_dir = root / "memory" / "notes"
    if notes_dir.is_dir():
        for note in sorted(notes_dir.rglob("*.md")):
            try:
                lines = note.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            in_summary = False
            for line in lines:
                bullet = _lesson_from_bullet(line)
                if bullet:
                    out.append(("notes", bullet))
                    continue
                stripped = line.strip()
                if stripped.startswith("## "):
                    in_summary = stripped.lower().startswith("## summary")
                    continue
                if in_summary and stripped and not stripped.startswith("#"):
                    out.append(("notes", stripped[:LESSON_MAX]))

    prompt_log = root / "state" / "prompt-log.jsonl"
    if prompt_log.is_file():
        try:
            raw_lines = prompt_log.read_text(encoding="utf-8").splitlines()
        except OSError:
            raw_lines = []
        for raw in raw_lines:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            prompt = str(row.get("prompt") or "").strip()
            if prompt:
                out.append(("prompt-log", prompt[:LESSON_MAX]))

    return out


def suggest_rules(
    project_root: Path,
    *,
    min_count: int = REPEAT_THRESHOLD,
    limit: int = MAX_SUGGESTIONS,
) -> list[dict[str, Any]]:
    """Return suggestion dicts for repeated fingerprints. Never writes."""
    rows = collect_source_lines(Path(project_root))
    if not rows:
        return []

    counts: Counter[str] = Counter()
    samples: dict[str, str] = {}
    sources: dict[str, set[str]] = defaultdict(set)

    for source, text in rows:
        key = fingerprint(text)
        if not key or len(key.split()) < 2:
            # Require at least two content words to avoid noise singles
            continue
        counts[key] += 1
        samples.setdefault(key, _trim(text))
        sources[key].add(source)

    ranked = sorted(
        ((fp, n) for fp, n in counts.items() if n >= min_count),
        key=lambda item: (-item[1], item[0]),
    )[: max(1, limit)]

    suggestions: list[dict[str, Any]] = []
    for fp, n in ranked:
        sample = samples[fp]
        suggestions.append(
            {
                "fingerprint": fp,
                "count": n,
                "sample": sample,
                "sources": sorted(sources[fp]),
                "wiki_note": sample,
                "agents_bullet": sample,
                "kind": "repeated_pattern",
            }
        )
    return suggestions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Suggest durable rules from repeated notes/prompts (no write)."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=REPEAT_THRESHOLD,
        help=f"Repeat threshold (default {REPEAT_THRESHOLD})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_SUGGESTIONS,
        help=f"Max suggestions (default {MAX_SUGGESTIONS})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON list",
    )
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    suggestions = suggest_rules(
        root, min_count=max(2, args.min_count), limit=max(1, args.limit)
    )
    if args.json:
        print(json.dumps({"suggestions": suggestions, "count": len(suggestions)}, indent=2))
        return 0
    if not suggestions:
        print("No repeated patterns (need 3+ matching notes or prompts).")
        return 0
    print(f"{len(suggestions)} suggestion(s) — propose only; wait for user YES before write:")
    for i, item in enumerate(suggestions, 1):
        print(f"{i}. ({item['count']}x, {','.join(item['sources'])}) {item['sample']}")
        print(f"   wiki/learn: {item['wiki_note']}")
        print(f"   AGENTS.md:  - {item['agents_bullet']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
