"""Disposable SQLite index over memory notes. Cache only — truth is the
markdown. Corrupt or missing db = silent rebuild. FTS5 when available,
LIKE fallback when the bundled sqlite lacks it (some Windows Pythons)."""

from __future__ import annotations

import math
import re
import sqlite3
import time
from pathlib import Path

DB_NAME = "memory.sqlite"
KIND_WEIGHTS = {"correction": 3.0, "want": 2.5, "decision": 2.5,
                "mistake": 2.0, "lesson": 2.0, "failure": 1.5}
HALF_LIFE_DAYS = 30.0

_KIND_RE = re.compile(r'kind:\s*"?(\w+)"?')
_COUNT_RE = re.compile(r"reinforcement_count:\s*(\d+)")
_CREATED_RE = re.compile(r'created:\s*"?([0-9T:\-.+Z ]+)"?')
_SUMMARY_RE = re.compile(r"## Summary\s+(.+?)(?:\n## |\Z)", re.S)


def _fts_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("CREATE VIRTUAL TABLE temp.__fts_probe USING fts5(x)")
        conn.execute("DROP TABLE temp.__fts_probe")
        return True
    except sqlite3.OperationalError:
        return False


def _parse_note(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if "status: revoked" in text or 'status: "revoked"' in text:
        return None
    kind = _KIND_RE.search(text)
    summary = _SUMMARY_RE.search(text)
    if not kind or not summary:
        return None
    count = _COUNT_RE.search(text)
    return {
        "kind": kind.group(1),
        "summary": summary.group(1).strip().splitlines()[0][:300],
        "reinforcement": int(count.group(1)) if count else 1,
        "mtime": path.stat().st_mtime,
    }


def _connect(memory_root: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(memory_root / DB_NAME))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def rebuild(memory_root: Path) -> dict:
    memory_root.mkdir(parents=True, exist_ok=True)
    db_path = memory_root / DB_NAME
    db_path.unlink(missing_ok=True)
    for suffix in ("-wal", "-shm"):
        Path(str(db_path) + suffix).unlink(missing_ok=True)
    conn = _connect(memory_root)
    backend = "fts5" if _fts_available(conn) else "like"
    with conn:
        if backend == "fts5":
            conn.execute(
                "CREATE VIRTUAL TABLE notes USING fts5(summary, kind UNINDEXED, "
                "reinforcement UNINDEXED, mtime UNINDEXED)")
        else:
            conn.execute(
                "CREATE TABLE notes(summary TEXT, kind TEXT, reinforcement INT, mtime REAL)")
        conn.execute("CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO meta VALUES('backend', ?)", (backend,))
        count = 0
        notes_dir = memory_root / "notes"
        if notes_dir.exists():
            for note_file in sorted(notes_dir.rglob("*.md")):
                row = _parse_note(note_file)
                if row is None:
                    continue
                conn.execute(
                    "INSERT INTO notes(summary, kind, reinforcement, mtime) VALUES(?,?,?,?)",
                    (row["summary"], row["kind"], row["reinforcement"], row["mtime"]))
                count += 1
    conn.close()
    return {"count": count, "backend": backend}


def _score(kind: str, reinforcement: int, mtime: float, base: float) -> float:
    age_days = max(0.0, (time.time() - mtime) / 86400.0)
    recency = 1.0 / (1.0 + age_days / HALF_LIFE_DAYS)
    weight = KIND_WEIGHTS.get(kind, 1.0)
    return base * weight * recency * (1.0 + math.log1p(reinforcement))


def search(memory_root: Path, query: str, limit: int = 3) -> list[dict]:
    query = (query or "").strip()
    if not query:
        return []
    for attempt in (1, 2):
        try:
            if not (memory_root / DB_NAME).exists():
                rebuild(memory_root)
            conn = _connect(memory_root)
            backend = conn.execute(
                "SELECT value FROM meta WHERE key='backend'").fetchone()[0]
            terms = [t for t in re.findall(r"[a-zA-Z0-9]{3,}", query)][:6]
            if not terms:
                conn.close()
                return []
            if backend == "fts5":
                match = " OR ".join(f'"{t}"' for t in terms)
                rows = conn.execute(
                    "SELECT summary, kind, reinforcement, mtime, bm25(notes) "
                    "FROM notes WHERE notes MATCH ? LIMIT 50", (match,)).fetchall()
                scored = [
                    {"summary": r[0], "kind": r[1],
                     "score": _score(r[1], r[2], r[3], base=max(0.1, -r[4]))}
                    for r in rows]
            else:
                clause = " OR ".join("summary LIKE ?" for _ in terms)
                rows = conn.execute(
                    f"SELECT summary, kind, reinforcement, mtime FROM notes WHERE {clause} LIMIT 50",
                    [f"%{t}%" for t in terms]).fetchall()
                scored = [
                    {"summary": r[0], "kind": r[1],
                     "score": _score(r[1], r[2], r[3], base=1.0)}
                    for r in rows]
            conn.close()
            scored.sort(key=lambda r: r["score"], reverse=True)
            return scored[:limit]
        except sqlite3.Error:
            (memory_root / DB_NAME).unlink(missing_ok=True)
            if attempt == 2:
                return []
        except Exception:
            return []
    return []
