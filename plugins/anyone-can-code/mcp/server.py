#!/usr/bin/env python3
"""
Anyone Can Code MCP memory server.

Portable linked-Markdown memory backend.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import uuid
import shutil
from pathlib import Path


SCOPES = {"project", "user", "shared"}
KINDS = {
    "archive",
    "decision",
    "evidence",
    "failure",
    "lesson",
    "preference",
    "mistake",
    "correction",
    "verified_fact",
    "project_convention",
    "pattern",
}
STATUSES = {"active", "downgraded", "revoked"}
DEFAULT_LIMIT = 5
NOTE_SCHEMA_VERSION = 1
SOURCE_TYPES = {"manual", "verified-work", "user-correction", "import", "hook", "unknown"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([a-z0-9_\-]{12,})"),
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def user_drawer_root() -> Path:
    override = os.environ.get("ACC_USER_MEMORY_ROOT")
    if override:
        return Path(override)
    # Legacy single-folder override (ACC_MCP_DATA_ROOT) still collapses both
    # drawers into one folder, so callers that pin the whole memory tree
    # (tests, migrations) keep working exactly as before the split.
    data_override = os.environ.get("ACC_MCP_DATA_ROOT")
    if data_override:
        return Path(data_override)
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "anyone-can-code" / "user-memory"
    return Path.home() / ".codex" / "anyone-can-code" / "user-memory"


def project_drawer_root(project_root_value: str | None) -> Path:
    override = os.environ.get("ACC_MCP_DATA_ROOT")
    if override:
        return Path(override)
    if project_root_value:
        return Path(project_root_value) / ".codex" / "anyone-can-code" / "memory"
    # Legacy fallback: old global pile keeps working when no project is known.
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "anyone-can-code" / "memory"
    return Path.home() / ".codex" / "anyone-can-code" / "memory"


def drawer_root(scope: str, project_root_value: str | None = None) -> Path:
    root = user_drawer_root() if scope == "user" else project_drawer_root(project_root_value)
    try:
        ensure_memory_layout(root)
    except OSError:
        root = Path(__file__).resolve().parent.parent / ".runtime" / "memory"
        ensure_memory_layout(root)
    return root


def data_root() -> Path:
    return project_drawer_root(None)


def ensure_data_root() -> Path:
    root = data_root()
    try:
        ensure_memory_layout(root)
        return root
    except OSError:
        fallback = Path(__file__).resolve().parent.parent / ".runtime" / "memory"
        ensure_memory_layout(fallback)
        return fallback


def ensure_memory_layout(root: Path) -> None:
    for relative in [
        "notes/project",
        "notes/user",
        "notes/shared",
        "notes/lessons",
        "notes/failures",
        "notes/decisions",
        "notes/evidence",
        "notes/archive",
        "index",
        "imports/snapshots",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)


def project_key(project_root: str) -> str:
    normalized = project_root.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def notes_root() -> Path:
    return ensure_data_root() / "notes"


def scope_dir(scope: str, project_root_value: str | None = None) -> Path:
    if scope not in SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    path = drawer_root(scope, project_root_value) / "notes" / scope
    path.mkdir(parents=True, exist_ok=True)
    return path


def note_path(scope: str, record_id: str, project_root_value: str | None = None) -> Path:
    return scope_dir(scope, project_root_value) / f"{safe_slug(record_id)}.md"


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-")
    return slug[:96] or str(uuid.uuid4())


def redact_secrets(text: str) -> tuple[str, bool]:
    redacted = text
    changed = False
    for pattern in SECRET_PATTERNS:
        redacted, count = pattern.subn(lambda match: match.group(1) + ": [REDACTED]" if match.groups() else "[REDACTED]", redacted)
        changed = changed or count > 0
    return redacted, changed


def yaml_scalar(value) -> str:
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(str(item)) for item in value) + "]"
    return json.dumps(str(value))


def render_frontmatter(record: dict) -> str:
    fields = [
        "id",
        "schema_version",
        "kind",
        "scope",
        "status",
        "created_at",
        "updated_at",
        "source",
        "provenance",
        "confidence",
        "reinforcement_count",
        "project_key",
        "project_root",
        "content_hash",
        "secret_redacted",
        "source_receipt",
        "related",
        "supersedes",
    ]
    lines = ["---"]
    for key in fields:
        if key in record:
            lines.append(f"{key}: {yaml_scalar(record[key])}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    if raw in {"true", "false"}:
        return raw == "true"
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        pass
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip('"')


def parse_markdown_note(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---\n"):
        return None
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        return None
    record: dict = {}
    for line in frontmatter.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        record[key.strip()] = parse_scalar(value)
    summary_match = re.search(r"## Summary\s+(.+?)(?:\n## |\Z)", body, re.S)
    evidence_match = re.search(r"## Evidence\s+(.+?)(?:\n## |\Z)", body, re.S)
    record["summary"] = (summary_match.group(1).strip() if summary_match else "").strip()
    record["evidence"] = (evidence_match.group(1).strip() if evidence_match else "").strip()
    record["_path"] = str(path)
    return record


def render_markdown_note(record: dict) -> str:
    title = record.get("title") or str(record.get("summary", "Memory")).splitlines()[0][:80]
    return (
        render_frontmatter(record)
        + f"# {title}\n\n"
        + "## Summary\n\n"
        + f"{record.get('summary', '').strip()}\n\n"
        + "## Evidence\n\n"
        + f"{record.get('evidence', '').strip() or 'Stored by Anyone Can Code.'}\n\n"
        + "## Links\n\n"
        + "- Related: " + ", ".join(record.get("related", [])) + "\n\n"
        + "## Receipt\n\n"
        + f"- Source: {record.get('source', 'unknown')}\n"
        + f"- Provenance: {record.get('provenance', 'unknown')}\n"
    )


def write_note(record: dict) -> Path:
    path = note_path(record["scope"], record["id"], record.get("project_root"))
    path.write_text(render_markdown_note(record), encoding="utf-8")
    return path


def load_all_records(project_root_value: str | None = None) -> list[dict]:
    rows: list[dict] = []
    roots = {user_drawer_root(), project_drawer_root(project_root_value)}
    for root in roots:
        for path in root.rglob("*.md"):
            row = parse_markdown_note(path)
            if row:
                rows.append(row)
    return rows


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}


def score_record(query: str, record: dict) -> float:
    haystack = " ".join(
        [
            str(record.get("summary", "")),
            str(record.get("kind", "")),
            str(record.get("source", "")),
            str(record.get("provenance", "")),
        ]
    )
    q_tokens = tokenize(query)
    h_tokens = tokenize(haystack)
    overlap = len(q_tokens & h_tokens)
    confidence = float(record.get("confidence", 0.2) or 0.2)
    reinforcement = int(record.get("reinforcement_count", 1) or 1)
    freshness = 0.2 if record.get("status", "active") == "active" else -1.0
    return overlap + confidence + min(reinforcement * 0.15, 1.5) + freshness


def normalize_record(arguments: dict) -> dict:
    scope = arguments.get("scope", "user")
    kind = arguments.get("kind", "pattern")
    status = arguments.get("status", "active")
    if scope not in SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    if kind not in KINDS:
        raise ValueError(f"Invalid kind: {kind}")
    if status not in STATUSES:
        raise ValueError(f"Invalid status: {status}")
    summary = str(arguments.get("summary", "")).strip()
    if not summary:
        raise ValueError("summary required")
    summary, secret_redacted = redact_secrets(summary)
    confidence = float(arguments.get("confidence", 0.35))
    confidence = max(0.0, min(1.0, confidence))
    record_id = str(arguments.get("id") or str(uuid.uuid4()))
    project_root_value = str(arguments.get("project_root", "")).strip()
    source = str(arguments.get("source", "unknown")).strip() or "unknown"
    source_type = source if source in SOURCE_TYPES else ("hook" if source.startswith("hook:") else "manual")
    content_hash = hashlib.sha256(f"{scope}|{kind}|{summary.lower()}|{project_root_value}".encode("utf-8")).hexdigest()
    return {
        "id": record_id,
        "schema_version": NOTE_SCHEMA_VERSION,
        "scope": scope,
        "kind": kind,
        "summary": summary,
        "confidence": confidence,
        "reinforcement_count": int(arguments.get("reinforcement_count", 1) or 1),
        "created_at": arguments.get("created_at") or utc_now(),
        "updated_at": arguments.get("updated_at") or arguments.get("last_seen_at") or utc_now(),
        "source": source_type,
        "provenance": source,
        "status": status,
        "project_key": project_key(project_root_value) if scope == "project" else "",
        "project_root": project_root_value,
        "content_hash": content_hash,
        "secret_redacted": secret_redacted,
        "source_receipt": str(arguments.get("source_receipt", "")).strip(),
        "related": arguments.get("related", []),
        "supersedes": arguments.get("supersedes", []),
        "evidence": str(arguments.get("evidence", "")).strip(),
    }


def merge_or_append(record: dict) -> dict:
    for row in load_all_records(record.get("project_root")):
        if (
            row.get("scope") == record["scope"]
            and row.get("kind") == record["kind"]
            and row.get("content_hash") == record["content_hash"]
        ):
            row["reinforcement_count"] = int(row.get("reinforcement_count", 1) or 1) + 1
            row["confidence"] = max(float(row.get("confidence", 0.2) or 0.2), record["confidence"])
            row["updated_at"] = utc_now()
            row["source"] = record["source"]
            row["provenance"] = record["provenance"]
            if row.get("status") == "revoked":
                row["status"] = "downgraded"
            write_note(row)
            return row
    write_note(record)
    return record


def active_rows(scope: str, project_root_value: str | None = None) -> list[dict]:
    rows = [row for row in load_all_records(project_root_value) if row.get("scope") == scope]
    if scope == "project":
        expected_key = project_key(project_root_value or "unknown-project")
        rows = [row for row in rows if row.get("project_key") == expected_key]
    return [row for row in rows if row.get("status", "active") != "revoked"]


def retrieve_context(arguments: dict) -> dict:
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query required")
    project_root_value = str(arguments.get("project_root", "")).strip() or None
    requested_limit = int(arguments.get("limit", DEFAULT_LIMIT) or DEFAULT_LIMIT)
    limit = max(1, min(requested_limit, 5))

    candidates: list[dict] = []
    if project_root_value:
        candidates.extend(active_rows("project", project_root_value))
    candidates.extend(active_rows("user"))
    candidates.extend(active_rows("shared"))

    ranked = sorted(
        candidates,
        key=lambda row: score_record(query, row),
        reverse=True,
    )
    seen_ids: set[str] = set()
    items: list[dict] = []
    for row in ranked:
        record_id = str(row.get("id"))
        if record_id in seen_ids:
            continue
        seen_ids.add(record_id)
        items.append(
            {
                "id": record_id,
                "scope": row.get("scope"),
                "kind": row.get("kind"),
                "summary": row.get("summary"),
                "confidence": row.get("confidence"),
                "reinforcement_count": row.get("reinforcement_count"),
                "status": row.get("status", "active"),
            }
        )
        if len(items) >= limit:
            break

    return {
        "mode": "portable-markdown",
        "query": query,
        "count": len(items),
        "items": items,
    }


def store_feedback(arguments: dict) -> dict:
    record = normalize_record(arguments)
    saved = merge_or_append(record)
    rebuild_index({})
    return {"stored": True, "mode": "portable-markdown", "record": saved, "path": str(note_path(saved["scope"], saved["id"], saved.get("project_root")))}


def promote_memory(arguments: dict) -> dict:
    record_id = str(arguments.get("id", "")).strip()
    if not record_id:
        raise ValueError("id required")
    project_root_value = str(arguments.get("project_root", "")).strip() or None
    for scope in ("project", "user", "shared"):
        for row in active_rows(scope, project_root_value):
            if row.get("id") == record_id:
                row["reinforcement_count"] = int(row.get("reinforcement_count", 1) or 1) + 1
                row["confidence"] = min(1.0, float(row.get("confidence", 0.2) or 0.2) + 0.15)
                row["updated_at"] = utc_now()
                row["status"] = "active"
                write_note(row)
                rebuild_index({})
                return {"promoted": True, "record": row}
    raise ValueError(f"Unknown id: {record_id}")


def revoke_memory(arguments: dict) -> dict:
    record_id = str(arguments.get("id", "")).strip()
    status = str(arguments.get("status", "revoked")).strip()
    if status not in {"downgraded", "revoked"}:
        raise ValueError("status must be downgraded or revoked")
    if not record_id:
        raise ValueError("id required")
    project_root_value = str(arguments.get("project_root", "")).strip() or None
    for row in load_all_records(project_root_value):
        if row.get("id") == record_id:
            row["status"] = status
            row["updated_at"] = utc_now()
            write_note(row)
            rebuild_index({})
            return {"updated": True, "record": row}
    raise ValueError(f"Unknown id: {record_id}")


def search_shared(arguments: dict) -> dict:
    arguments = dict(arguments)
    project_root_value = str(arguments.pop("project_root", "") or "").strip() or None
    rows = active_rows("shared", project_root_value)
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query required")
    limit = max(1, min(int(arguments.get("limit", DEFAULT_LIMIT) or DEFAULT_LIMIT), 5))
    ranked = sorted(rows, key=lambda row: score_record(query, row), reverse=True)
    items = [
        {
            "id": row.get("id"),
            "scope": row.get("scope"),
            "kind": row.get("kind"),
            "summary": row.get("summary"),
            "confidence": row.get("confidence"),
            "reinforcement_count": row.get("reinforcement_count"),
            "status": row.get("status", "active"),
        }
        for row in ranked[:limit]
    ]
    return {"query": query, "count": len(items), "items": items}


def rebuild_index(arguments: dict) -> dict:
    project_root_value = str((arguments or {}).get("project_root", "")).strip() or None
    rows = load_all_records(project_root_value)
    index_path = ensure_data_root() / "index" / "memory-index.json"
    payload = {
        "schema_version": 1,
        "rebuilt_at": utc_now(),
        "count": len(rows),
        "items": [
            {
                "id": row.get("id"),
                "scope": row.get("scope"),
                "kind": row.get("kind"),
                "status": row.get("status"),
                "summary": row.get("summary"),
                "path": row.get("_path"),
                "project_key": row.get("project_key", ""),
                "tokens": sorted(tokenize(str(row.get("summary", ""))))[:50],
            }
            for row in rows
        ],
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"rebuilt": True, "path": str(index_path), "count": len(rows)}


def iter_selected_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(str(raw)).expanduser()
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.jsonl")))
            files.extend(sorted(path.rglob("*.md")))
            files.extend(sorted(path.rglob("*.txt")))
    return files


def extract_session_summaries(path: Path, limit: int) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    summaries: list[str] = []
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            if len(summaries) >= limit:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            candidate = row.get("summary") or row.get("text") or row.get("content")
            if isinstance(candidate, str) and candidate.strip():
                summaries.append(candidate.strip()[:1200])
    else:
        chunks = [chunk.strip() for chunk in re.split(r"\n{2,}", text) if chunk.strip()]
        summaries.extend(chunk[:1200] for chunk in chunks[:limit])
    return summaries[:limit]


def write_import_receipt(receipt: dict, rollback: bool = False) -> Path:
    receipt_dir = ensure_data_root() / "imports"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-rollback" if rollback else ""
    receipt_path = receipt_dir / f"{receipt['receipt_id']}{suffix}.json"
    markdown_path = receipt_dir / f"{receipt['receipt_id']}{suffix}.md"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(
        "\n".join(
            [
                "# Anyone Can Code Memory Import Receipt",
                "",
                f"- Status: `{receipt['status']}`",
                f"- Operation: `{receipt['operation']}`",
                f"- Scope: `{receipt['scope']}`",
                f"- Sources: {len(receipt['sources'])}",
                f"- Snapshots or backups: {len(receipt.get('snapshots', [])) + len(receipt.get('backups', []))}",
                f"- Imported: {receipt['imported_count']}",
                f"- Skipped duplicate: {receipt['skipped_count']}",
                f"- Source files deleted: no",
                f"- Error: {receipt.get('error', '') or 'none'}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    receipt["receipt_path"] = str(receipt_path)
    receipt["receipt_markdown"] = str(markdown_path)
    return receipt_path


def restore_notes_from_snapshot(snapshot: Path, notes_path: Path, notes_existed: bool) -> None:
    if notes_path.exists():
        shutil.rmtree(notes_path)
    if notes_existed:
        shutil.copytree(snapshot, notes_path)
    else:
        notes_path.mkdir(parents=True, exist_ok=True)


def import_selected_files(arguments: dict, operation: str) -> dict:
    paths = arguments.get("paths") or arguments.get("sources") or []
    if not isinstance(paths, list) or not paths:
        raise ValueError("paths required")
    scope = str(arguments.get("scope", "project")).strip()
    if scope not in SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    project_root_value = str(arguments.get("project_root", "")).strip()
    dry_run = bool(arguments.get("dry_run", False))
    per_file_limit = max(1, min(int(arguments.get("per_file_limit", 5) or 5), 25))
    files = iter_selected_files(paths)
    receipt_id = f"import-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    imported: list[dict] = []
    snapshots: list[str] = []
    backups: list[str] = []
    skipped: list[dict] = []
    root = ensure_data_root()
    notes_path = root / "notes"
    rollback_root = root / "imports" / "transactions" / receipt_id
    notes_snapshot = rollback_root / "notes-before"
    notes_existed = notes_path.exists()
    writes_started = False

    receipt = {
        "receipt_id": receipt_id,
        "timestamp": utc_now(),
        "operation": operation,
        "status": "preview" if dry_run else "started",
        "scope": scope,
        "project_key": project_key(project_root_value) if scope == "project" else "",
        "sources": [str(path) for path in files],
        "snapshots": snapshots,
        "backups": backups,
        "dry_run": dry_run,
        "imported_count": 0,
        "skipped_count": 0,
        "imported": imported,
        "skipped": skipped,
    }

    if dry_run:
        for source_file in files:
            for summary in extract_session_summaries(source_file, per_file_limit):
                record = normalize_record(
                    {
                        "scope": scope,
                        "kind": "pattern",
                        "summary": summary,
                        "confidence": 0.35,
                        "source": "import",
                        "project_root": project_root_value,
                    }
                )
                imported.append({"id": record["id"], "source": str(source_file), "dry_run": True})
        receipt["imported_count"] = len(imported)
        return receipt

    try:
        rollback_root.mkdir(parents=True, exist_ok=True)
        if notes_existed:
            shutil.copytree(notes_path, notes_snapshot)

        source_folder = "backups" if operation == "legacy-jsonl" else "snapshots"
        source_snapshot_dir = root / "imports" / source_folder / receipt_id
        source_snapshot_dir.mkdir(parents=True, exist_ok=True)
        for index, source_file in enumerate(files):
            snapshot_path = source_snapshot_dir / f"{index:04d}-{safe_slug(source_file.name)}"
            shutil.copy2(source_file, snapshot_path)
            if operation == "legacy-jsonl":
                backups.append(str(snapshot_path))
            else:
                snapshots.append(str(snapshot_path))

        existing_hashes = {
            str(row.get("content_hash"))
            for row in load_all_records()
            if row.get("content_hash")
        }
        for source_file in files:
            for summary in extract_session_summaries(source_file, per_file_limit):
                payload = {
                    "scope": scope,
                    "kind": "pattern",
                    "summary": summary,
                    "confidence": 0.35,
                    "source": "import",
                    "source_receipt": receipt_id,
                    "evidence": f"Imported from {source_file}. Receipt: {receipt_id}.",
                    "project_root": project_root_value,
                }
                record = normalize_record(payload)
                record["provenance"] = str(source_file)
                if record["content_hash"] in existing_hashes:
                    skipped.append({"content_hash": record["content_hash"], "source": str(source_file)})
                    continue
                writes_started = True
                saved = merge_or_append(record)
                existing_hashes.add(record["content_hash"])
                imported.append(
                    {
                        "id": saved.get("id"),
                        "path": str(note_path(saved["scope"], saved["id"], saved.get("project_root"))),
                        "source": str(source_file),
                        "source_receipt": receipt_id,
                    }
                )

        rebuild_index({})
        verified = all(
            (parsed := parse_markdown_note(Path(item["path"])))
            and parsed.get("content_hash") in existing_hashes
            and parsed.get("source_receipt") == receipt_id
            for item in imported
        )
        if not verified:
            raise RuntimeError("Markdown verification failed")
        receipt["status"] = "verified"
        receipt["imported_count"] = len(imported)
        receipt["skipped_count"] = len(skipped)
        write_import_receipt(receipt)
        shutil.rmtree(rollback_root, ignore_errors=True)
        return receipt
    except Exception as exc:
        if writes_started:
            try:
                restore_notes_from_snapshot(notes_snapshot, notes_path, notes_existed)
                rebuild_index({})
            except Exception as rollback_exc:
                receipt["rollback_error"] = str(rollback_exc)
        receipt["status"] = "rolled_back"
        receipt["error"] = str(exc)
        receipt["imported_count"] = 0
        receipt["skipped_count"] = len(skipped)
        rollback_path = write_import_receipt(receipt, rollback=True)
        receipt["rollback_receipt_path"] = str(rollback_path)
        return receipt


def import_session_files(arguments: dict) -> dict:
    return import_selected_files(arguments, "session-import")


def migrate_legacy_jsonl(arguments: dict) -> dict:
    return import_selected_files(arguments, "legacy-jsonl")


TOOLS = {
    "retrieve_context": {
        "description": "Find top reinforced memories for one task. Project first, then user, then shared.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "project_root": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["query"],
        },
        "handler": retrieve_context,
    },
    "store_feedback": {
        "description": "Store one reinforced memory item with scope, kind, confidence, and source.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "enum": sorted(SCOPES)},
                "kind": {"type": "string", "enum": sorted(KINDS)},
                "summary": {"type": "string"},
                "confidence": {"type": "number"},
                "source": {"type": "string"},
                "project_root": {"type": "string"},
            },
            "required": ["scope", "kind", "summary"],
        },
        "handler": store_feedback,
    },
    "promote_memory": {
        "description": "Increase trust for one memory item after repeated proof.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "project_root": {"type": "string"},
            },
            "required": ["id"],
        },
        "handler": promote_memory,
    },
    "revoke_memory": {
        "description": "Downgrade or revoke stale memory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "status": {"type": "string", "enum": ["downgraded", "revoked"]},
                "project_root": {"type": "string"},
            },
            "required": ["id"],
        },
        "handler": revoke_memory,
    },
    "search_shared": {
        "description": "Search only shared cross-project memory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 5},
                "project_root": {"type": "string"},
            },
            "required": ["query"],
        },
        "handler": search_shared,
    },
    "rebuild_index": {
        "description": "Rebuild disposable search index from Markdown notes.",
        "inputSchema": {
            "type": "object",
            "properties": {"project_root": {"type": "string"}},
        },
        "handler": rebuild_index,
    },
    "import_session_files": {
        "description": "Import user-selected session files into scoped Markdown notes with receipt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "scope": {"type": "string", "enum": sorted(SCOPES)},
                "project_root": {"type": "string"},
                "dry_run": {"type": "boolean"},
                "per_file_limit": {"type": "integer", "minimum": 1, "maximum": 25},
            },
            "required": ["paths"],
        },
        "handler": import_session_files,
    },
}


def make_response(message_id, result=None, error=None):
    payload = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return payload


def handle_request(message: dict) -> dict | None:
    method = message.get("method")
    params = message.get("params", {}) or {}
    message_id = message.get("id")

    if method == "initialize":
        return make_response(
            message_id,
            {
                "protocolVersion": "2025-06-18",
                "serverInfo": {"name": "anyone-can-code-memory", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return make_response(message_id, {})
    if method == "tools/list":
        return make_response(
            message_id,
            {
                "tools": [
                    {
                        "name": name,
                        "description": tool["description"],
                        "inputSchema": tool["inputSchema"],
                    }
                    for name, tool in TOOLS.items()
                ]
            },
        )
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {}) or {}
        tool = TOOLS.get(name)
        if not tool:
            return make_response(message_id, error={"code": -32601, "message": f"Unknown tool: {name}"})
        try:
            result = tool["handler"](arguments)
        except Exception as exc:  # pragma: no cover - stdio server best effort
            print(f"tool error {name}: {exc}", file=sys.stderr)
            return make_response(message_id, error={"code": -32000, "message": str(exc)})
        return make_response(
            message_id,
            {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "structuredContent": result,
            },
        )
    return make_response(message_id, error={"code": -32601, "message": f"Unknown method: {method}"})


def main() -> None:
    ensure_data_root()
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"invalid json: {exc}", file=sys.stderr)
            continue
        response = handle_request(message)
        if response is None:
            continue
        sys.stdout.write(json.dumps(response, ensure_ascii=True) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
