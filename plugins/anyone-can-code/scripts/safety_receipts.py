#!/usr/bin/env python3
"""Readable receipts, security approvals, and rollback gates for ACC."""

from __future__ import annotations

import json
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


NAMESPACE = Path(".codex") / "anyone-can-code"
REMOTE_ACTIONS = {"push", "pull-request", "merge", "publish", "release", "tag", "deploy"}
RISKY_ACTIONS = {"delete", "overwrite", "migration", "install", "external-share", "remote"}
PRODUCTION_EXTRA_RISKY = {"install", "migrate", "seed", "deploy", "release", "tag"}


class SafetyGateError(RuntimeError):
    """Raised when an action is missing approval, rollback, or authority."""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def receipts_dir(repo_root: Path) -> Path:
    return repo_root / NAMESPACE / "artifacts" / "receipts"


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-")
    return slug[:80] or "action"


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


def classify_action(action: dict[str, Any], production_mode: bool = False) -> dict[str, Any]:
    action_type = str(action.get("type") or "").strip()
    command = str(action.get("command") or "").lower()
    remote = bool(action.get("remote")) or action_type in REMOTE_ACTIONS
    remote = remote or any(token in command for token in ("git push", "gh pr", "npm publish"))
    risky = bool(action.get("risky")) or action_type in RISKY_ACTIONS or remote
    risky = risky or any(token in command for token in ("remove-item", "rm -rf", "git reset --hard"))
    force_blocked = production_mode and "--force" in command
    production_caution = production_mode and (action_type in PRODUCTION_EXTRA_RISKY or risky)
    return {
        "remote": remote,
        "risky": risky,
        "approval_required": risky or remote or production_caution,
        "rollback_required": risky and not remote,
        "sandbox_required": True,
        "production_caution": production_caution,
        "force_blocked": force_blocked,
    }


def validate_action_authority(action: dict[str, Any]) -> dict[str, Any]:
    production_mode = bool(
        action.get("production_mode")
        if action.get("production_mode") is not None
        else action.get("production")
    )
    classification = classify_action(action, production_mode=production_mode)
    approval = str(action.get("user_approval") or "").strip()
    rollback = str(action.get("rollback") or "").strip()
    remote_evidence = str(action.get("remote_authority") or "").strip()
    sandbox = str(action.get("sandbox") or "codex-native").strip()

    missing: list[str] = []
    if classification.get("force_blocked"):
        missing.append("force flag blocked in production")
    if classification["approval_required"] and not approval:
        missing.append("exact user approval")
    if classification["rollback_required"] and not rollback:
        missing.append("backup or rollback path")
    if classification["remote"] and not remote_evidence:
        missing.append("remote authority evidence")
    if not sandbox:
        missing.append("native Codex sandbox or approval context")

    return {
        "allowed": not missing,
        "missing": missing,
        "classification": classification,
        "sandbox": sandbox,
        "approval": approval,
        "rollback": rollback,
        "remote_authority": remote_evidence,
    }


def render_receipt(receipt: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ACC Action Receipt",
            "",
            f"- ID: `{receipt['id']}`",
            f"- Action: {receipt['action']}",
            f"- Status: `{receipt['status']}`",
            f"- Risky: {'yes' if receipt['classification']['risky'] else 'no'}",
            f"- Remote: {'yes' if receipt['classification']['remote'] else 'no'}",
            f"- Approval: {receipt.get('approval') or 'not supplied'}",
            f"- Rollback: {receipt.get('rollback') or 'not required or not supplied'}",
            f"- Remote authority: {receipt.get('remote_authority') or 'not required or not supplied'}",
            f"- Sandbox: {receipt.get('sandbox') or 'unknown'}",
            f"- Missing: {', '.join(receipt.get('missing', [])) or 'none'}",
            f"- Evidence: {', '.join(receipt.get('evidence', [])) or 'none'}",
            f"- Created: {receipt['created_at']}",
            "",
        ]
    )


def write_action_receipt(
    repo_root: Path,
    action: dict[str, Any],
    *,
    status: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    authority = validate_action_authority(action)
    action_name = str(action.get("name") or action.get("type") or "action").strip()
    receipt_id = f"{utc_now().replace(':', '').replace('-', '')}-{_safe_slug(action_name)}-{uuid.uuid4().hex[:8]}"
    receipt = {
        "id": receipt_id,
        "schema_version": 1,
        "created_at": utc_now(),
        "action": action_name,
        "status": status,
        "classification": authority["classification"],
        "missing": authority["missing"],
        "approval": authority["approval"],
        "rollback": authority["rollback"],
        "remote_authority": authority["remote_authority"],
        "sandbox": authority["sandbox"],
        "evidence": evidence or [],
    }
    root = receipts_dir(repo_root)
    json_path = root / f"{receipt_id}.json"
    markdown_path = root / f"{receipt_id}.md"
    _write_text_atomic(json_path, json.dumps(receipt, indent=2) + "\n")
    _write_text_atomic(markdown_path, render_receipt(receipt))
    receipt["receipt_path"] = str(json_path)
    receipt["receipt_markdown"] = str(markdown_path)
    return receipt


def prepare_action(
    repo_root: Path,
    action: dict[str, Any],
    *,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    authority = validate_action_authority(action)
    status = "approved" if authority["allowed"] else "blocked"
    receipt = write_action_receipt(repo_root, action, status=status, evidence=evidence)
    if not authority["allowed"]:
        raise SafetyGateError(
            "Action blocked; missing " + ", ".join(authority["missing"])
        )
    return receipt
