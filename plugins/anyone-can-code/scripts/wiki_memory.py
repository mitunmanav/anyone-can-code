#!/usr/bin/env python3
"""Karpathy-style wiki layer for ACC project memory.

Raw sources stay immutable. Durable facts live in notes/. Human navigation is
wiki/index.md + wiki/log.md. Machine cache stays in index/memory-index.json.

Never writes to Codex native ~/.codex/memories/.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import time
from pathlib import Path


BRIEF_CHAR_CAP = 800
INDEX_MAX_LINES = 80
LOG_MAX_BYTES = 200_000


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_wiki_layout(memory_root: Path) -> dict[str, Path]:
    """Create raw/ + wiki/ with seed index.md and log.md."""
    memory_root = Path(memory_root)
    raw = memory_root / "raw"
    wiki = memory_root / "wiki"
    notes = memory_root / "notes"
    index_dir = memory_root / "index"
    imports = memory_root / "imports"
    for path in (raw, wiki, notes, index_dir, imports):
        path.mkdir(parents=True, exist_ok=True)
    index_md = wiki / "index.md"
    log_md = wiki / "log.md"
    if not index_md.exists():
        index_md.write_text(
            "# Project wiki index\n\n"
            "ACC maintains this file. One line per strong note.\n\n"
            "## Pages\n\n"
            "- (empty — save a lesson or decision first)\n",
            encoding="utf-8",
        )
    if not log_md.exists():
        log_md.write_text(
            "# Project wiki log\n\n"
            "Append-only. ACC writes what changed.\n\n",
            encoding="utf-8",
        )
    return {
        "memory": memory_root,
        "raw": raw,
        "wiki": wiki,
        "notes": notes,
        "index_md": index_md,
        "log_md": log_md,
        "index_dir": index_dir,
        "imports": imports,
    }


def _note_summary(path: Path) -> tuple[str, str, str]:
    """Return (kind, summary, relative_path_hint)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ("", "", path.name)
    if "status: revoked" in text or 'status: "revoked"' in text:
        return ("revoked", "", path.name)
    kind_m = re.search(r"(?m)^kind:\s*\"?([A-Za-z0-9_]+)\"?", text)
    kind = kind_m.group(1) if kind_m else "note"
    summary_m = re.search(r"## Summary\s+(.+?)(?:\n## |\Z)", text, re.S)
    if summary_m:
        summary = summary_m.group(1).strip().splitlines()[0][:120]
    else:
        title_m = re.search(r"(?m)^#\s+(.+)$", text)
        summary = (title_m.group(1).strip() if title_m else path.stem)[:120]
    rel = path.name
    try:
        # prefer notes/scope/file.md style if under notes
        parts = path.parts
        if "notes" in parts:
            i = parts.index("notes")
            rel = "/".join(parts[i:])
    except Exception:
        pass
    return (kind, summary, rel)


def collect_note_rows(memory_root: Path) -> list[dict]:
    notes_dir = Path(memory_root) / "notes"
    rows: list[dict] = []
    if not notes_dir.exists():
        return rows
    for path in sorted(notes_dir.rglob("*.md")):
        kind, summary, rel = _note_summary(path)
        if kind == "revoked" or not summary:
            continue
        rows.append(
            {
                "path": path,
                "kind": kind,
                "summary": summary,
                "rel": rel,
            }
        )
    return rows


def rebuild_human_index(memory_root: Path) -> dict:
    """Rewrite wiki/index.md from notes Markdown."""
    layout = ensure_wiki_layout(memory_root)
    rows = collect_note_rows(memory_root)
    lines = [
        "# Project wiki index",
        "",
        f"Rebuilt: {utc_now()}",
        f"Active notes: {len(rows)}",
        "",
        "ACC owns this catalog. Facts live under `notes/`. Raw sources under `raw/`.",
        "Native Codex memories are not used.",
        "",
        "## Pages",
        "",
    ]
    if not rows:
        lines.append("- (empty — save a lesson or decision first)")
    else:
        for row in rows[:INDEX_MAX_LINES]:
            lines.append(f"- [{row['kind']}] [{row['summary']}](../{row['rel']})")
        if len(rows) > INDEX_MAX_LINES:
            lines.append(f"- … and {len(rows) - INDEX_MAX_LINES} more (open notes/)")
    lines.append("")
    layout["index_md"].write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "rebuilt": True,
        "path": str(layout["index_md"]),
        "count": len(rows),
    }


def append_log(memory_root: Path, action: str, detail: str) -> str:
    layout = ensure_wiki_layout(memory_root)
    log_path = layout["log_md"]
    line = f"- {utc_now()} · {action}: {detail.strip()[:200]}\n"
    try:
        if log_path.exists() and log_path.stat().st_size > LOG_MAX_BYTES:
            # Keep last half of log to bound growth.
            text = log_path.read_text(encoding="utf-8")
            log_path.write_text(
                "# Project wiki log\n\n(truncated)\n\n" + text[-LOG_MAX_BYTES // 2 :],
                encoding="utf-8",
            )
    except OSError:
        pass
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return line.strip()


def session_brief(memory_root: Path, max_chars: int = BRIEF_CHAR_CAP) -> str:
    """Short context for SessionStart. Index-first, never whole vault."""
    memory_root = Path(memory_root)
    ensure_wiki_layout(memory_root)
    index_md = memory_root / "wiki" / "index.md"
    try:
        text = index_md.read_text(encoding="utf-8")
    except OSError:
        return ""
    page_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("- [") and "empty" not in line.lower()
    ]
    if not page_lines:
        return ""
    out = ["Wiki brief (ACC project notebook; native Codex memory OFF):"]
    total = len(out[0])
    for line in page_lines[:12]:
        entry = f"  {line}"
        if total + len(entry) + 1 > max_chars:
            break
        out.append(entry)
        total += len(entry) + 1
    return "\n".join(out)


def lint_wiki(memory_root: Path) -> dict:
    """Health check: empty index, missing files, revoked noise, orphan raw."""
    memory_root = Path(memory_root)
    layout = ensure_wiki_layout(memory_root)
    issues: list[dict] = []
    rows = collect_note_rows(memory_root)
    if not rows:
        issues.append(
            {
                "code": "empty_wiki",
                "severity": "info",
                "detail": "No active notes yet. Save a decision or lesson.",
            }
        )
    # Orphan related wiki-style links in note bodies
    known = {row["path"].stem.lower() for row in rows}
    known |= {row["rel"].lower() for row in rows}
    for row in rows:
        try:
            body = row["path"].read_text(encoding="utf-8")
        except OSError:
            continue
        for match in re.findall(r"\[\[([^\]]+)\]\]", body):
            target = match.split("|")[0].strip().lower()
            slug = Path(target).stem.lower()
            if slug and slug not in known and target not in known:
                issues.append(
                    {
                        "code": "orphan_link",
                        "severity": "warn",
                        "detail": f"{row['rel']} links to [[{match}]] which has no note",
                    }
                )
    # Raw files with no mention in notes (info only)
    raw_files = list(layout["raw"].rglob("*")) if layout["raw"].exists() else []
    raw_files = [p for p in raw_files if p.is_file()]
    if raw_files and not rows:
        issues.append(
            {
                "code": "raw_without_wiki",
                "severity": "info",
                "detail": f"{len(raw_files)} raw file(s) but no wiki notes yet",
            }
        )
    # Stale: very low confidence revoked leftovers still present as files
    revoked = 0
    notes_dir = memory_root / "notes"
    if notes_dir.exists():
        for path in notes_dir.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if "status: revoked" in text or 'status: "revoked"' in text:
                revoked += 1
    if revoked:
        issues.append(
            {
                "code": "revoked_present",
                "severity": "info",
                "detail": f"{revoked} revoked note file(s) still on disk (ok; not in index)",
            }
        )
    return {
        "ok": not any(i["severity"] == "warn" for i in issues),
        "issue_count": len(issues),
        "active_notes": len(rows),
        "issues": issues[:25],
        "index_path": str(layout["index_md"]),
        "log_path": str(layout["log_md"]),
    }


def ingest_raw(
    memory_root: Path,
    source: str | Path,
    *,
    consent: bool = False,
) -> dict:
    """Copy a user-selected source into raw/. Never rewrites existing raw bytes of different content with same name unless new hash name."""
    if not consent:
        return {
            "ok": False,
            "error": "consent required before raw ingest",
            "hint": "Pass consent=true after the user says yes.",
        }
    memory_root = Path(memory_root)
    layout = ensure_wiki_layout(memory_root)
    src = Path(source).expanduser()
    if not src.is_file():
        return {"ok": False, "error": f"not a file: {src}"}
    try:
        data = src.read_bytes()
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    digest = hashlib.sha256(data).hexdigest()[:12]
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", src.name).strip("-")[:80] or "source"
    dest_name = f"{digest}-{safe_name}"
    dest = layout["raw"] / dest_name
    if dest.exists():
        append_log(memory_root, "raw-skip", f"already have {dest_name}")
        return {"ok": True, "path": str(dest), "skipped": True, "content_hash": digest}
    shutil.copy2(src, dest)
    append_log(memory_root, "raw-ingest", dest_name)
    return {
        "ok": True,
        "path": str(dest),
        "skipped": False,
        "content_hash": digest,
        "note": "Raw stored. AI must not rewrite this file. Use store_feedback to make a wiki note.",
    }


def sync_after_store(memory_root: Path, summary: str, kind: str = "note") -> dict:
    """After a durable note write: refresh human index + log."""
    memory_root = Path(memory_root)
    ensure_wiki_layout(memory_root)
    index_result = rebuild_human_index(memory_root)
    log_line = append_log(memory_root, "save", f"[{kind}] {summary[:160]}")
    return {
        "index": index_result,
        "log_line": log_line,
    }


