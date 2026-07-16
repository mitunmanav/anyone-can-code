"""Rule-from-repetition: a lesson seen 3+ times in memory notes becomes a
promotion proposal. Propose once; the user says yes/no. Never auto-promote —
`approve` runs only after an explicit yes."""

from __future__ import annotations

import json
from pathlib import Path

import state

REPEAT_THRESHOLD = 3
LESSON_MAX = 200


def _normalize(lesson: str) -> str:
    words = "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in lesson)
    return " ".join(words.split())


def _proposed_ledger(repo_root: Path) -> Path:
    return state.ensure_project_layout(repo_root)["memory"] / "promotion-proposals.json"


def _rules_file(repo_root: Path) -> Path:
    return state.ensure_project_layout(repo_root)["memory"] / "rules.md"


def _count_lessons(repo_root: Path) -> dict[str, str]:
    """Return {normalized: original} for lessons seen REPEAT_THRESHOLD+ times."""
    notes_dir = state.ensure_project_layout(repo_root)["memory_notes"]
    counts: dict[str, int] = {}
    originals: dict[str, str] = {}
    if not notes_dir.exists():
        return {}
    for note in notes_dir.rglob("*.md"):
        try:
            lines = note.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            text = line.strip()
            if not text.startswith("-"):
                continue
            lesson = text.lstrip("-* ").strip()[:LESSON_MAX]
            key = _normalize(lesson)
            if not key:
                continue
            counts[key] = counts.get(key, 0) + 1
            originals.setdefault(key, lesson)
    return {k: originals[k] for k, n in counts.items() if n >= REPEAT_THRESHOLD}


def pending_proposals(repo_root: Path) -> list[str]:
    """New proposals only — each repeated lesson is proposed exactly once."""
    ledger_path = _proposed_ledger(repo_root)
    try:
        proposed = set(json.loads(ledger_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        proposed = set()
    proposals: list[str] = []
    repeated = _count_lessons(repo_root)
    for key, lesson in repeated.items():
        if key in proposed:
            continue
        proposed.add(key)
        proposals.append(
            f"Lesson seen 3+ times: \"{lesson}\". "
            "Make it a permanent rule shown every session? yes/no."
        )
    if proposals:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(sorted(proposed)), encoding="utf-8")
    return proposals


def approve(repo_root: Path, lesson: str) -> Path:
    """User said yes: append the rule. Call ONLY after explicit approval."""
    rules_path = _rules_file(repo_root)
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    existing = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    line = f"- {lesson.strip()[:LESSON_MAX]}"
    if line not in existing:
        header = "" if existing else "# Permanent rules (user approved)\n"
        rules_path.write_text(existing + header + line + "\n", encoding="utf-8")
    return rules_path


def approved_rules(repo_root: Path, limit: int = 5) -> list[str]:
    rules_path = _rules_file(repo_root)
    if not rules_path.exists():
        return []
    try:
        lines = rules_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return [l.strip() for l in lines if l.strip().startswith("-")][-limit:]
