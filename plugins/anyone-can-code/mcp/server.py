#!/usr/bin/env python3
"""
Anyone Can Code MCP memory server.

One local stdio server. Durable memory stays here, not in project files.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path


SCOPES = {"project", "user", "shared"}
KINDS = {
    "preference",
    "mistake",
    "correction",
    "verified_fact",
    "project_convention",
    "pattern",
}
STATUSES = {"active", "downgraded", "revoked"}
DEFAULT_LIMIT = 5


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def data_root() -> Path:
    override = os.environ.get("ACC_MCP_DATA_ROOT")
    if override:
        return Path(override)
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "anyone-can-code" / "mcp-memory"
    return Path.home() / ".codex" / "anyone-can-code" / "mcp-memory"


def ensure_data_root() -> Path:
    root = data_root()
    try:
        root.mkdir(parents=True, exist_ok=True)
        return root
    except OSError:
        fallback = Path(__file__).resolve().parent.parent / ".runtime" / "mcp-memory"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def project_key(project_root: str) -> str:
    normalized = project_root.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def store_path(scope: str, project_root: str | None = None) -> Path:
    root = ensure_data_root()
    if scope == "project":
        key = project_key(project_root or "unknown-project")
        return root / "project" / f"{key}.jsonl"
    return root / scope / "memory.jsonl"


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def save_records(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}


def score_record(query: str, record: dict) -> float:
    haystack = " ".join(
        [
            str(record.get("summary", "")),
            str(record.get("kind", "")),
            str(record.get("source", "")),
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
    confidence = float(arguments.get("confidence", 0.35))
    confidence = max(0.0, min(1.0, confidence))
    return {
        "id": arguments.get("id") or str(uuid.uuid4()),
        "scope": scope,
        "kind": kind,
        "summary": summary,
        "confidence": confidence,
        "reinforcement_count": int(arguments.get("reinforcement_count", 1) or 1),
        "last_seen_at": arguments.get("last_seen_at") or utc_now(),
        "source": str(arguments.get("source", "unknown")).strip() or "unknown",
        "status": status,
    }


def merge_or_append(path: Path, record: dict) -> dict:
    rows = load_records(path)
    for row in rows:
        if (
            row.get("scope") == record["scope"]
            and row.get("kind") == record["kind"]
            and row.get("summary", "").strip().lower() == record["summary"].strip().lower()
        ):
            row["reinforcement_count"] = int(row.get("reinforcement_count", 1) or 1) + 1
            row["confidence"] = max(float(row.get("confidence", 0.2) or 0.2), record["confidence"])
            row["last_seen_at"] = utc_now()
            row["source"] = record["source"]
            if row.get("status") == "revoked":
                row["status"] = "downgraded"
            save_records(path, rows)
            return row
    rows.append(record)
    save_records(path, rows)
    return record


def active_rows(scope: str, project_root_value: str | None = None) -> list[dict]:
    rows = load_records(store_path(scope, project_root_value))
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
        "mode": "mcp-first",
        "query": query,
        "count": len(items),
        "items": items,
    }


def store_feedback(arguments: dict) -> dict:
    project_root_value = str(arguments.get("project_root", "")).strip() or None
    record = normalize_record(arguments)
    path = store_path(record["scope"], project_root_value if record["scope"] == "project" else None)
    saved = merge_or_append(path, record)
    return {"stored": True, "record": saved}


def promote_memory(arguments: dict) -> dict:
    record_id = str(arguments.get("id", "")).strip()
    if not record_id:
        raise ValueError("id required")
    for scope in ("project", "user", "shared"):
        paths = []
        if scope == "project":
            paths = list((ensure_data_root() / "project").glob("*.jsonl"))
        else:
            paths = [store_path(scope)]
        for path in paths:
            rows = load_records(path)
            changed = False
            for row in rows:
                if row.get("id") == record_id:
                    row["reinforcement_count"] = int(row.get("reinforcement_count", 1) or 1) + 1
                    row["confidence"] = min(1.0, float(row.get("confidence", 0.2) or 0.2) + 0.15)
                    row["last_seen_at"] = utc_now()
                    row["status"] = "active"
                    changed = True
                    save_records(path, rows)
                    return {"promoted": True, "record": row}
            if changed:
                break
    raise ValueError(f"Unknown id: {record_id}")


def revoke_memory(arguments: dict) -> dict:
    record_id = str(arguments.get("id", "")).strip()
    status = str(arguments.get("status", "revoked")).strip()
    if status not in {"downgraded", "revoked"}:
        raise ValueError("status must be downgraded or revoked")
    if not record_id:
        raise ValueError("id required")
    for scope in ("project", "user", "shared"):
        paths = []
        if scope == "project":
            paths = list((ensure_data_root() / "project").glob("*.jsonl"))
        else:
            paths = [store_path(scope)]
        for path in paths:
            rows = load_records(path)
            for row in rows:
                if row.get("id") == record_id:
                    row["status"] = status
                    row["last_seen_at"] = utc_now()
                    save_records(path, rows)
                    return {"updated": True, "record": row}
    raise ValueError(f"Unknown id: {record_id}")


def search_shared(arguments: dict) -> dict:
    arguments = dict(arguments)
    arguments.pop("project_root", None)
    rows = active_rows("shared")
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
            "properties": {"id": {"type": "string"}},
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
            },
            "required": ["query"],
        },
        "handler": search_shared,
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
