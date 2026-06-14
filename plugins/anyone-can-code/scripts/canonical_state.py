#!/usr/bin/env python3
"""Transactional canonical workflow state for Anyone Can Code."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


NAMESPACE = Path(".codex") / "anyone-can-code"

DEFAULT_STATE: dict[str, Any] = {
    "schema_version": 5,
    "transaction_id": "",
    "workflow_owner": "acc",
    "active_goal": "",
    "active_task": "",
    "decisions": [],
    "boundaries": [],
    "progress": [],
    "verification": {
        "level": "unverified",
        "evidence": [],
        "stale": False,
    },
    "failures": [],
    "warnings": [],
    "next_action": "",
    "plan": [],
    "tasks": [],
    "task_claims": {},
    "subagent_policy": {
        "requires_explicit_user_request": True,
        "requires_codex_need": True,
        "max_parallel": 2,
        "return_to": "acc",
    },
    "active_task_capsule": {},
    "recovery": {
        "last_transition": "",
        "capsule_saved_at": "",
        "uncertainty": [],
    },
    "updated_at": "",
}


class StateTransactionError(RuntimeError):
    """Raised when canonical state and its derived views cannot update together."""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def state_root(repo_root: Path) -> Path:
    return repo_root / NAMESPACE


def state_paths(repo_root: Path) -> dict[str, Path]:
    root = state_root(repo_root)
    return {
        "workflow": root / "state" / "workflow.json",
        "status": root / "state" / "state-current.md",
        "queue": root / "state" / "task-queue.md",
        "snapshot": root / "state" / "session-snapshot.md",
        "history": root / "state" / "state-history.jsonl",
        "resume": root / "artifacts" / "resume-note.md",
        "guidance": root / "artifacts" / "active-guidance.md",
        "capsule": root / "artifacts" / "active-task-capsule.md",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return copy.deepcopy(DEFAULT_STATE)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return copy.deepcopy(DEFAULT_STATE)
    if not isinstance(value, dict):
        return copy.deepcopy(DEFAULT_STATE)
    merged = copy.deepcopy(DEFAULT_STATE)
    merged.update(value)
    verification = copy.deepcopy(DEFAULT_STATE["verification"])
    if isinstance(value.get("verification"), dict):
        verification.update(value["verification"])
    merged["verification"] = verification
    recovery = copy.deepcopy(DEFAULT_STATE["recovery"])
    if isinstance(value.get("recovery"), dict):
        recovery.update(value["recovery"])
    merged["recovery"] = recovery
    return merged


def read_canonical_state(repo_root: Path) -> dict[str, Any]:
    return _read_json(state_paths(repo_root)["workflow"])


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _snapshot(paths: list[Path]) -> dict[Path, bytes | None]:
    return {
        path: path.read_bytes() if path.exists() else None
        for path in paths
    }


def _restore(snapshot: dict[Path, bytes | None]) -> None:
    for path, content in snapshot.items():
        try:
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        except OSError:
            continue


def _render_status(state: dict[str, Any]) -> str:
    verification = state["verification"]
    return "\n".join(
        [
            "# ACC Current State",
            "",
            f"- Transaction: {state['transaction_id']}",
            f"- Workflow owner: {state['workflow_owner']}",
            f"- Goal: {state['active_goal'] or 'Not set'}",
            f"- Active task: {state['active_task'] or 'Not set'}",
            f"- Verification: {verification['level']}",
            f"- Verification stale: {'yes' if verification['stale'] else 'no'}",
            f"- Next action: {state['next_action'] or 'Not set'}",
            f"- Updated: {state['updated_at']}",
            "",
        ]
    )


def _render_queue(state: dict[str, Any]) -> str:
    lines = [
        "# ACC Task Queue",
        "",
        f"Transaction: {state['transaction_id']}",
        "",
    ]
    for task in state.get("tasks", []):
        if isinstance(task, dict):
            lines.append(
                f"- [{task.get('state', 'in scope')}] {task.get('name', 'Unnamed task')}"
            )
        else:
            lines.append(f"- [in scope] {task}")
    if not state.get("tasks"):
        lines.append("- No tasks recorded.")
    return "\n".join(lines) + "\n"


def _render_resume(state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ACC Resume Note",
            "",
            f"Transaction: {state['transaction_id']}",
            "",
            f"Goal: {state['active_goal'] or 'Not set'}",
            f"Task: {state['active_task'] or 'Not set'}",
            f"Next: {state['next_action'] or 'Not set'}",
            "",
        ]
    )


def _render_guidance(state: dict[str, Any]) -> str:
    lines = [
        "# ACC Active Guidance",
        "",
        f"Transaction: {state['transaction_id']}",
        f"Workflow owner: {state['workflow_owner']}",
        "",
        "## Active Plan",
    ]
    lines.extend(f"- {item}" for item in state.get("plan", []))
    if not state.get("plan"):
        lines.append("- No plan recorded.")
    lines.extend(["", "## Boundaries"])
    lines.extend(f"- {item}" for item in state.get("boundaries", []))
    if not state.get("boundaries"):
        lines.append("- No boundaries recorded.")
    return "\n".join(lines) + "\n"


def _render_snapshot(state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ACC Session Snapshot",
            "",
            f"Transaction: {state['transaction_id']}",
            f"Goal: {state['active_goal'] or 'Not set'}",
            f"Task: {state['active_task'] or 'Not set'}",
            f"Next: {state['next_action'] or 'Not set'}",
            f"Verification: {state['verification']['level']}",
            "",
        ]
    )


def _build_active_task_capsule(state: dict[str, Any]) -> dict[str, Any]:
    verification = state.get("verification") or {}
    return {
        "transaction_id": state["transaction_id"],
        "saved_at": state["updated_at"],
        "goal": state.get("active_goal", ""),
        "task": state.get("active_task", ""),
        "decisions": copy.deepcopy(state.get("decisions") or []),
        "boundaries": copy.deepcopy(state.get("boundaries") or []),
        "evidence": copy.deepcopy(verification.get("evidence") or []),
        "next_action": state.get("next_action", ""),
    }


def _render_capsule(state: dict[str, Any]) -> str:
    capsule = state["active_task_capsule"]
    lines = [
        "# ACC Active Task Capsule",
        "",
        f"Transaction: {capsule['transaction_id']}",
        f"Saved: {capsule['saved_at']}",
        f"Goal: {capsule['goal'] or 'Unknown'}",
        f"Task: {capsule['task'] or 'Unknown'}",
        f"Next: {capsule['next_action'] or 'Unknown'}",
        "",
        "## Decisions",
    ]
    lines.extend(f"- {item}" for item in capsule["decisions"])
    if not capsule["decisions"]:
        lines.append("- None recorded.")
    lines.extend(["", "## Boundaries"])
    lines.extend(f"- {item}" for item in capsule["boundaries"])
    if not capsule["boundaries"]:
        lines.append("- None recorded.")
    lines.extend(["", "## Evidence"])
    lines.extend(f"- {item}" for item in capsule["evidence"])
    if not capsule["evidence"]:
        lines.append("- None recorded.")
    return "\n".join(lines) + "\n"


def update_canonical_state(
    repo_root: Path,
    updates: dict[str, Any],
    *,
    history_entry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = state_paths(repo_root)
    current = read_canonical_state(repo_root)
    updated = copy.deepcopy(current)
    updated.update(copy.deepcopy(updates))
    if isinstance(updates.get("verification"), dict):
        verification = copy.deepcopy(current.get("verification") or {})
        verification.update(copy.deepcopy(updates["verification"]))
        updated["verification"] = verification
    updated["schema_version"] = 5
    updated["transaction_id"] = uuid.uuid4().hex
    updated["updated_at"] = utc_now()
    updated["active_task_capsule"] = _build_active_task_capsule(updated)
    recovery = copy.deepcopy(DEFAULT_STATE["recovery"])
    if isinstance(updated.get("recovery"), dict):
        recovery.update(updated["recovery"])
    recovery["capsule_saved_at"] = updated["updated_at"]
    updated["recovery"] = recovery

    history_text = ""
    if paths["history"].exists():
        history_text = paths["history"].read_text(encoding="utf-8")
    if history_entry:
        row = {
            "timestamp": updated["updated_at"],
            "transaction_id": updated["transaction_id"],
            **history_entry,
        }
        history_text += json.dumps(row, sort_keys=True) + "\n"

    writes = {
        paths["workflow"]: json.dumps(updated, indent=2) + "\n",
        paths["status"]: _render_status(updated),
        paths["queue"]: _render_queue(updated),
        paths["resume"]: _render_resume(updated),
        paths["guidance"]: _render_guidance(updated),
        paths["snapshot"]: _render_snapshot(updated),
        paths["capsule"]: _render_capsule(updated),
    }
    if history_entry:
        writes[paths["history"]] = history_text

    snapshot = _snapshot(list(writes))
    try:
        for path, text in writes.items():
            _write_text_atomic(path, text)
    except Exception as exc:
        _restore(snapshot)
        raise StateTransactionError(f"State transaction rolled back: {exc}") from exc
    return updated


def prepare_context_transition(repo_root: Path, *, transition: str) -> dict[str, Any]:
    current = read_canonical_state(repo_root)
    recovery = copy.deepcopy(current.get("recovery") or {})
    recovery.update(
        {
            "last_transition": str(transition).strip(),
            "uncertainty": [],
        }
    )
    return update_canonical_state(
        repo_root,
        {"recovery": recovery},
        history_entry={
            "event": "context-transition",
            "transition": str(transition).strip(),
            "status": "capsule-saved",
        },
    )


def _recovery_uncertainty(repo_root: Path, state: dict[str, Any]) -> list[str]:
    uncertainty = []
    required = (
        ("active_goal", "active goal missing"),
        ("active_task", "active task missing"),
        ("next_action", "next action missing"),
    )
    for key, message in required:
        if not str(state.get(key) or "").strip():
            uncertainty.append(message)

    transaction_id = str(state.get("transaction_id") or "")
    for key in ("status", "queue", "snapshot", "resume", "guidance", "capsule"):
        path = state_paths(repo_root)[key]
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            uncertainty.append(f"{path.name} missing or unreadable")
            continue
        if not transaction_id or transaction_id not in text:
            uncertainty.append(f"{path.name} transaction mismatch")
    return uncertainty


def recover_from_canonical_state(
    repo_root: Path,
    *,
    repair: bool = False,
) -> dict[str, Any]:
    workflow_path = state_paths(repo_root)["workflow"]
    if not workflow_path.exists():
        return {
            "status": "uncertain",
            "source": "canonical-state",
            "transaction_id": "",
            "capsule": {},
            "uncertainty": ["canonical workflow state missing"],
            "repaired": False,
        }
    try:
        raw = json.loads(workflow_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "status": "uncertain",
            "source": "canonical-state",
            "transaction_id": "",
            "capsule": {},
            "uncertainty": ["canonical workflow state unreadable"],
            "repaired": False,
        }
    if not isinstance(raw, dict):
        return {
            "status": "uncertain",
            "source": "canonical-state",
            "transaction_id": "",
            "capsule": {},
            "uncertainty": ["canonical workflow state invalid"],
            "repaired": False,
        }

    state = read_canonical_state(repo_root)
    uncertainty = _recovery_uncertainty(repo_root, state)
    if repair and any("transaction mismatch" in item or "unreadable" in item for item in uncertainty):
        state = update_canonical_state(
            repo_root,
            {},
            history_entry={
                "event": "recovery",
                "status": "derived-views-rebuilt",
            },
        )
        uncertainty = _recovery_uncertainty(repo_root, state)
        repaired = True
    else:
        repaired = False

    return {
        "status": "ready" if not uncertainty else "uncertain",
        "source": "canonical-state",
        "transaction_id": state.get("transaction_id", ""),
        "capsule": copy.deepcopy(state.get("active_task_capsule") or {}),
        "uncertainty": uncertainty,
        "repaired": repaired,
    }


def apply_scope_change(
    repo_root: Path,
    *,
    new_goal: str,
    new_task: str,
    reason: str,
) -> dict[str, Any]:
    current = read_canonical_state(repo_root)
    verification = copy.deepcopy(current.get("verification") or {})
    verification.update(
        {
            "level": "unverified",
            "evidence": [],
            "stale": True,
            "stale_reason": "Scope changed",
        }
    )
    return update_canonical_state(
        repo_root,
        {
            "active_goal": str(new_goal).strip(),
            "active_task": str(new_task).strip(),
            "verification": verification,
        },
        history_entry={
            "event": "scope-change",
            "status": "superseded",
            "reason": str(reason).strip(),
            "old_goal": current.get("active_goal", ""),
            "old_task": current.get("active_task", ""),
            "new_goal": str(new_goal).strip(),
            "new_task": str(new_task).strip(),
        },
    )
