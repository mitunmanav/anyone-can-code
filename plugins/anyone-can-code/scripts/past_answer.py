"""Answer "what did we decide about X?" from local memory: notes, decisions,
turn ledger. Pure text search over plugin-local files — no dependencies."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import state

STOPWORDS = {
    "what", "did", "we", "do", "the", "a", "an", "about", "decide", "decided",
    "which", "when", "why", "how", "is", "was", "you", "i", "to", "for", "of",
    "on", "in", "and", "or", "it", "that", "this", "pick", "picked", "choose",
    "chose", "use", "used", "say", "said", "tell", "told",
}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
MAX_HITS = 5
TEXT_MAX = 200


def _keywords(query: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", query.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _file_date(path: Path, fallback_text: str = "") -> str:
    for candidate in (path.stem, fallback_text):
        match = DATE_RE.search(candidate)
        if match:
            return match.group(0)
    try:
        ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return ts.strftime("%Y-%m-%d")
    except OSError:
        return "unknown-date"


def _score(text: str, keywords: set[str]) -> int:
    low = text.lower()
    return sum(1 for k in keywords if k in low)


def search_past(repo_root: Path, query: str, limit: int = MAX_HITS) -> list[dict]:
    """Return [{date, source, text}] best-first; [] means honest no-record."""
    keywords = _keywords(query)
    if not keywords:
        return []
    layout = state.ensure_project_layout(repo_root)
    hits: list[tuple[int, str, dict]] = []

    notes_dir = layout["memory_notes"]
    if notes_dir.exists():
        for note in notes_dir.rglob("*.md"):
            try:
                lines = note.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line in lines:
                text = line.strip().lstrip("-* ").strip()
                if not text:
                    continue
                score = _score(text, keywords)
                if score:
                    date = _file_date(note, text)
                    source = str(note.relative_to(notes_dir))
                    hits.append((score, date, {
                        "date": date, "source": source, "text": text[:TEXT_MAX],
                    }))

    ledger = layout["state"] / "turn-ledger.jsonl"
    if ledger.exists():
        try:
            lines = ledger.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for raw in lines:
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            text = " ".join(str(v) for v in entry.values() if isinstance(v, str))
            score = _score(text, keywords)
            if score:
                match = DATE_RE.search(str(entry.get("ts", "")))
                date = match.group(0) if match else _file_date(ledger)
                hits.append((score, date, {
                    "date": date, "source": "turn-ledger", "text": text[:TEXT_MAX],
                }))

    hits.sort(key=lambda h: (h[0], h[1]), reverse=True)
    return [h[2] for h in hits[:limit]]


def main() -> None:
    query = " ".join(sys.argv[1:])
    root = Path.cwd()
    results = search_past(root, query)
    if not results:
        print("No record found in memory for that question.")
        return
    for hit in results:
        print(f"{hit['date']} [{hit['source']}] {hit['text']}")


if __name__ == "__main__":
    main()
