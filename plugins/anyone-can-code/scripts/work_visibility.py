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
USAGE_CHECKPOINT_PERCENT = 85
USAGE_SPLIT_PERCENT = 90
USAGE_STOP_PERCENT = 94
PATCH_MAX_FAILED_ATTEMPTS = 2
PLATFORM_MECHANICS_TERMS = (
    "codex desktop",
    "hook",
    "plugin runtime",
    "installed cache",
    "runtime cache",
    "windows launch",
    "powershell",
    "ui lifecycle",
    "telemetry",
    "otlp",
    "log parsing",
    "logs",
    "mcp",
    "tool plumbing",
    "app-server",
)


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


def assess_usage_checkpoint(
    *,
    primary_percent: int | float | None = None,
) -> dict[str, Any]:
    """Return the required session action for reported primary usage."""

    percent = None if primary_percent is None else float(primary_percent)
    action = "continue"
    checkpoint_required = False
    split_required = False
    stop_required = False
    continue_without_user_choice = True
    message = "Usage below checkpoint threshold."

    if percent is None:
        action = "check-usage"
        continue_without_user_choice = False
        message = "Usage percentage unknown; check usage before long work."
    elif percent >= USAGE_STOP_PERCENT:
        action = "stop-now"
        checkpoint_required = True
        split_required = True
        stop_required = True
        continue_without_user_choice = False
        message = "Stop now, checkpoint, and continue only after explicit user choice."
    elif percent >= USAGE_SPLIT_PERCENT:
        action = "split"
        checkpoint_required = True
        split_required = True
        continue_without_user_choice = False
        message = "Create a checkpoint and split before more work."
    elif percent >= USAGE_CHECKPOINT_PERCENT:
        action = "checkpoint"
        checkpoint_required = True
        continue_without_user_choice = False
        message = "Create a checkpoint before continuing long work."

    return {
        "reported_primary_percent": primary_percent,
        "checkpoint_threshold_percent": USAGE_CHECKPOINT_PERCENT,
        "split_threshold_percent": USAGE_SPLIT_PERCENT,
        "stop_threshold_percent": USAGE_STOP_PERCENT,
        "action": action,
        "checkpoint_required": checkpoint_required,
        "split_required": split_required,
        "stop_required": stop_required,
        "continue_without_user_choice": continue_without_user_choice,
        "message": message,
        "uncertainty": "Uses reported percentage from Codex usage records; exact live usage may differ.",
    }


def assess_patch_retry(
    *,
    failed_attempts: int = 0,
    last_patch_failed: bool = False,
    exact_target_reread: bool = False,
    max_failed_attempts: int = PATCH_MAX_FAILED_ATTEMPTS,
) -> dict[str, Any]:
    """Return whether a patch attempt may proceed after prior misses."""

    attempts = max(0, int(failed_attempts))
    can_apply_patch = True
    reread_required = False
    action = "apply"
    message = "Patch may proceed."

    if attempts >= max_failed_attempts:
        can_apply_patch = False
        action = "stop-and-replan"
        message = "Patch retry limit reached; stop and replan before editing."
    elif last_patch_failed and not exact_target_reread:
        can_apply_patch = False
        reread_required = True
        action = "reread-exact-target"
        message = "Reread the exact target block before retrying the patch."
    elif last_patch_failed and exact_target_reread:
        action = "retry-once"
        message = "Exact target was reread; one bounded retry may proceed."

    return {
        "can_apply_patch": can_apply_patch,
        "action": action,
        "failed_attempts": attempts,
        "max_failed_attempts": max_failed_attempts,
        "last_patch_failed": bool(last_patch_failed),
        "exact_target_reread": bool(exact_target_reread),
        "reread_required": reread_required,
        "message": message,
        "rule": "after a failed patch, reread exact target before retry",
    }


def assess_mechanics_docs_gate(
    request: str,
    *,
    docs_brief: str = "",
    controlled_proof: bool = False,
    uncertainty: str = "",
) -> dict[str, Any]:
    """Gate platform-mechanics changes on docs/source or controlled proof."""

    text = str(request or "").lower()
    matched_terms = [term for term in PLATFORM_MECHANICS_TERMS if term in text]
    docs = str(docs_brief or "").strip()
    uncertainty_text = str(uncertainty or "").strip()
    platform_mechanics = bool(matched_terms)

    if not platform_mechanics:
        return {
            "can_change_code": True,
            "action": "proceed",
            "platform_mechanics": False,
            "docs_brief_required": False,
            "matched_terms": [],
            "evidence_source": "not-platform-mechanics",
            "uncertainty_required": False,
            "rule": "platform mechanics changes require docs brief before code",
        }
    if docs:
        return {
            "can_change_code": True,
            "action": "proceed",
            "platform_mechanics": True,
            "docs_brief_required": True,
            "matched_terms": matched_terms,
            "evidence_source": "docs-brief",
            "docs_brief": docs,
            "uncertainty_required": False,
            "rule": "platform mechanics changes require docs brief before code",
        }
    if controlled_proof and uncertainty_text:
        return {
            "can_change_code": True,
            "action": "proceed-with-uncertainty",
            "platform_mechanics": True,
            "docs_brief_required": True,
            "matched_terms": matched_terms,
            "evidence_source": "controlled-proof-with-uncertainty",
            "uncertainty": uncertainty_text,
            "uncertainty_required": True,
            "rule": "platform mechanics changes require docs brief before code",
        }
    if controlled_proof:
        action = "record-uncertainty"
        message = "Controlled proof exists, but uncertainty must be recorded before code changes."
    else:
        action = "write-docs-brief"
        message = "Write a docs brief from official docs/source before code changes."
    return {
        "can_change_code": False,
        "action": action,
        "platform_mechanics": True,
        "docs_brief_required": True,
        "matched_terms": matched_terms,
        "evidence_source": "missing",
        "uncertainty_required": True,
        "message": message,
        "rule": "platform mechanics changes require docs brief before code",
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
    high_usage = assess_usage_checkpoint(primary_percent=90)
    patch_retry = assess_patch_retry(
        failed_attempts=1,
        last_patch_failed=True,
        exact_target_reread=False,
    )
    mechanics_gate = assess_mechanics_docs_gate("Change Codex Desktop hook launch")
    if budget["estimated_tokens"] <= 0:
        return False, "usage estimate failed"
    if depth["depth"] != "cheap":
        return False, "cheap check selection failed"
    if high_usage["action"] != "split" or not high_usage["split_required"]:
        return False, "high usage checkpoint failed"
    if patch_retry["can_apply_patch"] or not patch_retry["reread_required"]:
        return False, "patch retry reread discipline failed"
    if mechanics_gate["can_change_code"] or mechanics_gate["action"] != "write-docs-brief":
        return False, "mechanics docs gate failed"
    return True, "usage budgets, compact receipts, background bounds, high-usage split checkpoints, patch retry rereads, and mechanics docs gate available"
