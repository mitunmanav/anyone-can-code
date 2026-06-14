#!/usr/bin/env python3
"""Usage-budget estimates, compact evidence receipts, and visible background work."""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


NAMESPACE = Path(".codex") / "anyone-can-code"
DEFAULT_TOKEN_CHAR_RATIO = 4
DEFAULT_LARGE_READ_TOKENS = 6000
DEFAULT_LOOP_ITEMS = 25
MAX_COMPACT_CHARS = 1600


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    with open(handle, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    Path(temp_name).replace(path)


def _safe_slug(value: str) -> str:
    keep = []
    for char in value.strip():
        if char.isalnum() or char in "._-":
            keep.append(char)
        elif char.isspace():
            keep.append("-")
    slug = "".join(keep).strip("-")
    return slug[:80] or "work"


def artifacts_root(repo_root: Path) -> Path:
    return repo_root / NAMESPACE / "artifacts"


def estimate_context_cost(
    *,
    text: str = "",
    paths: list[Path] | None = None,
    loop_items: int = 0,
    large_read_tokens: int = DEFAULT_LARGE_READ_TOKENS,
    loop_limit: int = DEFAULT_LOOP_ITEMS,
) -> dict[str, Any]:
    """Return a cheap pre-read estimate with explicit uncertainty."""

    file_bytes = 0
    unreadable: list[str] = []
    for path in paths or []:
        try:
            file_bytes += path.stat().st_size
        except OSError:
            unreadable.append(str(path))

    estimated_chars = len(text) + file_bytes
    estimated_tokens = math.ceil(estimated_chars / DEFAULT_TOKEN_CHAR_RATIO)
    warnings: list[str] = []
    if estimated_tokens >= large_read_tokens:
        warnings.append(
            "Large context read likely; estimate is approximate before tokenization."
        )
    if loop_items > loop_limit:
        warnings.append(
            "Large loop likely; item count is known but per-item output is uncertain."
        )
    if unreadable:
        warnings.append(
            "Some files were unreadable, so context estimate is incomplete."
        )
    return {
        "estimated_tokens": estimated_tokens,
        "estimated_chars": estimated_chars,
        "file_bytes": file_bytes,
        "loop_items": loop_items,
        "large_read": estimated_tokens >= large_read_tokens,
        "large_loop": loop_items > loop_limit,
        "uncertainty": "Estimate uses file bytes and 4 chars per token; exact usage may differ.",
        "warnings": warnings,
        "unreadable": unreadable,
    }


def choose_check_depth(
    *,
    changed_files: int,
    shared_behavior: bool = False,
    user_visible: bool = False,
    risky_action: bool = False,
) -> dict[str, Any]:
    risk_reasons: list[str] = []
    if changed_files > 5:
        risk_reasons.append("many changed files")
    if shared_behavior:
        risk_reasons.append("shared behavior")
    if user_visible:
        risk_reasons.append("user-visible behavior")
    if risky_action:
        risk_reasons.append("risky action")
    depth = "deep" if risk_reasons else "cheap"
    checks = ["syntax", "focused tests"]
    if depth == "deep":
        checks.extend(["full tests", "doctor", "flow validation"])
    return {
        "depth": depth,
        "reason": risk_reasons or ["small local change"],
        "checks": checks,
    }


def compact_tool_evidence(
    *,
    tool: str,
    command: str = "",
    exit_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
    max_chars: int = MAX_COMPACT_CHARS,
) -> dict[str, Any]:
    combined = "\n".join(part for part in [stdout, stderr] if part)
    digest = hashlib.sha256(combined.encode("utf-8", errors="replace")).hexdigest()
    clipped = combined[:max_chars]
    return {
        "tool": tool,
        "command": command,
        "exit_code": exit_code,
        "output_sha256": digest,
        "output_chars": len(combined),
        "compacted": len(combined) > len(clipped),
        "excerpt": clipped,
        "uncertainty": "Receipt stores compact output, not full transcript.",
    }


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        f"# ACC {receipt['kind'].replace('-', ' ').title()} Receipt",
        "",
        f"- ID: `{receipt['id']}`",
        f"- Status: `{receipt['status']}`",
        f"- Created: {receipt['created_at']}",
    ]
    if receipt["kind"] == "tool-evidence":
        evidence = receipt["evidence"]
        lines.extend(
            [
                f"- Tool: {evidence['tool']}",
                f"- Exit code: {evidence.get('exit_code')}",
                f"- Output chars: {evidence['output_chars']}",
                f"- Compacted: {'yes' if evidence['compacted'] else 'no'}",
                f"- Uncertainty: {evidence['uncertainty']}",
            ]
        )
    if receipt["kind"] == "background-work":
        work = receipt["work"]
        lines.extend(
            [
                f"- Name: {work['name']}",
                f"- Purpose: {work['purpose']}",
                f"- State: {work['state']}",
                f"- Stop command: {work['stop_command']}",
                f"- Limit seconds: {work['limit_seconds']}",
                f"- Limit steps: {work['limit_steps']}",
                f"- Stopping condition: {work['stopping_condition']}",
            ]
        )
    if receipt["kind"] == "usage-budget":
        budget = receipt["budget"]
        lines.extend(
            [
                f"- Estimated tokens: {budget['estimated_tokens']}",
                f"- Loop items: {budget['loop_items']}",
                f"- Large read: {'yes' if budget['large_read'] else 'no'}",
                f"- Large loop: {'yes' if budget['large_loop'] else 'no'}",
                f"- Uncertainty: {budget['uncertainty']}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_receipt(repo_root: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_id = receipt.setdefault(
        "id",
        f"{utc_now().replace(':', '').replace('-', '')}-{_safe_slug(receipt['kind'])}-{uuid.uuid4().hex[:8]}",
    )
    receipt.setdefault("created_at", utc_now())
    root = artifacts_root(repo_root) / "receipts"
    json_path = root / f"{receipt_id}.json"
    markdown_path = root / f"{receipt_id}.md"
    _write_text_atomic(json_path, json.dumps(receipt, indent=2) + "\n")
    _write_text_atomic(markdown_path, render_receipt(receipt))
    receipt["receipt_path"] = str(json_path)
    receipt["receipt_markdown"] = str(markdown_path)
    return receipt


def write_usage_budget_receipt(repo_root: Path, budget: dict[str, Any]) -> dict[str, Any]:
    return write_receipt(
        repo_root,
        {
            "kind": "usage-budget",
            "status": "estimated",
            "budget": budget,
        },
    )


def write_tool_evidence_receipt(
    repo_root: Path,
    *,
    tool: str,
    command: str = "",
    exit_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
) -> dict[str, Any]:
    return write_receipt(
        repo_root,
        {
            "kind": "tool-evidence",
            "status": "recorded",
            "evidence": compact_tool_evidence(
                tool=tool,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
            ),
        },
    )


def start_background_work(
    repo_root: Path,
    *,
    name: str,
    purpose: str,
    stop_command: str,
    stopping_condition: str,
    limit_seconds: int,
    limit_steps: int,
    scope: str = "project",
) -> dict[str, Any]:
    missing = []
    if not purpose.strip():
        missing.append("purpose")
    if not stop_command.strip():
        missing.append("stop command")
    if not stopping_condition.strip():
        missing.append("stopping condition")
    if limit_seconds <= 0:
        missing.append("time limit")
    if limit_steps <= 0:
        missing.append("step limit")
    status = "blocked" if missing else "started"
    receipt = write_receipt(
        repo_root,
        {
            "kind": "background-work",
            "status": status,
            "work": {
                "name": name,
                "purpose": purpose,
                "scope": scope,
                "state": status,
                "started_at": utc_now(),
                "stop_command": stop_command,
                "stopping_condition": stopping_condition,
                "limit_seconds": limit_seconds,
                "limit_steps": limit_steps,
                "missing": missing,
            },
        },
    )
    return receipt


def complete_background_work(
    repo_root: Path,
    receipt_id: str,
    *,
    status: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    path = artifacts_root(repo_root) / "receipts" / f"{receipt_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = status
    payload["completed_at"] = utc_now()
    payload.setdefault("work", {})["state"] = status
    payload["evidence"] = evidence or []
    return write_receipt(repo_root, payload)


def smoke_check(repo_root: Path) -> tuple[bool, str]:
    budget = estimate_context_cost(text="x" * 100, loop_items=2)
    depth = choose_check_depth(changed_files=1)
    if budget["estimated_tokens"] <= 0:
        return False, "usage estimate failed"
    if depth["depth"] != "cheap":
        return False, "cheap check selection failed"
    return True, "usage budgets, compact receipts, and background bounds available"
