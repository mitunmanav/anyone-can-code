#!/usr/bin/env python3
"""Bounded task and subagent coordination for Anyone Can Code."""

from __future__ import annotations

import copy
import re
import sys
import uuid
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import canonical_state


TASK_STATUSES = {"todo", "in_progress", "blocked", "done"}


class TaskCoordinationError(RuntimeError):
    """Raised when task coordination would create unsafe or duplicate work."""


def _task_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(name).strip().lower()).strip("-")
    return slug or "task"


def normalize_task(task: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(task, str):
        task = {"name": task}
    if not isinstance(task, dict):
        raise TaskCoordinationError("Task must be text or object")
    name = str(task.get("name") or task.get("id") or "").strip()
    if not name:
        raise TaskCoordinationError("Task name required")
    status = str(task.get("status") or task.get("state") or "todo").strip()
    if status not in TASK_STATUSES:
        raise TaskCoordinationError(f"Unsupported task status: {status}")
    owner = str(task.get("owner") or "acc").strip() or "acc"
    dependencies = task.get("dependencies") or task.get("depends_on") or []
    if not isinstance(dependencies, list):
        raise TaskCoordinationError("Task dependencies must be a list")
    evidence = task.get("evidence") or []
    if not isinstance(evidence, list):
        raise TaskCoordinationError("Task evidence must be a list")
    return {
        "id": str(task.get("id") or _task_id(name)),
        "name": name,
        "dependencies": [str(item).strip() for item in dependencies if str(item).strip()],
        "owner": owner,
        "status": status,
        "evidence": [str(item).strip() for item in evidence if str(item).strip()],
        "claim_id": str(task.get("claim_id") or "").strip(),
        "claimed_by": str(task.get("claimed_by") or "").strip(),
        "claimed_at": str(task.get("claimed_at") or "").strip(),
        "completed_at": str(task.get("completed_at") or "").strip(),
    }


def _find_task(tasks: list[dict[str, Any]], task_id_or_name: str) -> int:
    needle = str(task_id_or_name).strip()
    for index, task in enumerate(tasks):
        if task.get("id") == needle or task.get("name") == needle:
            return index
    raise TaskCoordinationError(f"Task not found: {needle}")


def set_task_queue(repo_root: Path, tasks: list[dict[str, Any] | str]) -> dict[str, Any]:
    normalized = [normalize_task(task) for task in tasks]
    return canonical_state.update_canonical_state(
        repo_root,
        {"tasks": normalized},
        history_entry={
            "event": "task-queue-updated",
            "status": "recorded",
            "task_count": len(normalized),
        },
    )


def claim_task(
    repo_root: Path,
    task_id_or_name: str,
    *,
    owner: str,
    claim_id: str | None = None,
) -> dict[str, Any]:
    state = canonical_state.read_canonical_state(repo_root)
    tasks = [normalize_task(task) for task in state.get("tasks", [])]
    index = _find_task(tasks, task_id_or_name)
    task = copy.deepcopy(tasks[index])
    existing_claim = task.get("claim_id")
    if task["status"] == "done":
        raise TaskCoordinationError("Done task cannot be claimed again")
    if task["status"] == "in_progress" and existing_claim and existing_claim != claim_id:
        raise TaskCoordinationError("Task already claimed")
    if any(dep not in {item["id"] for item in tasks if item["status"] == "done"} for dep in task["dependencies"]):
        raise TaskCoordinationError("Task dependencies not done")

    active_claim = claim_id or uuid.uuid4().hex
    task.update(
        {
            "owner": str(owner).strip() or "acc",
            "status": "in_progress",
            "claim_id": active_claim,
            "claimed_by": str(owner).strip() or "acc",
            "claimed_at": canonical_state.utc_now(),
        }
    )
    tasks[index] = task
    claims = copy.deepcopy(state.get("task_claims") or {})
    claims[task["id"]] = {
        "claim_id": active_claim,
        "owner": task["owner"],
        "claimed_at": task["claimed_at"],
    }
    return canonical_state.update_canonical_state(
        repo_root,
        {
            "active_task": task["name"],
            "tasks": tasks,
            "task_claims": claims,
        },
        history_entry={
            "event": "task-claimed",
            "status": "active",
            "task": task["id"],
            "owner": task["owner"],
            "claim_id": active_claim,
        },
    )


def complete_task(
    repo_root: Path,
    task_id_or_name: str,
    *,
    claim_id: str,
    evidence: list[str],
) -> dict[str, Any]:
    state = canonical_state.read_canonical_state(repo_root)
    tasks = [normalize_task(task) for task in state.get("tasks", [])]
    index = _find_task(tasks, task_id_or_name)
    task = copy.deepcopy(tasks[index])
    if task.get("claim_id") != claim_id:
        raise TaskCoordinationError("Task claim mismatch")
    task["status"] = "done"
    task["completed_at"] = canonical_state.utc_now()
    task["evidence"] = [*task["evidence"], *[str(item).strip() for item in evidence if str(item).strip()]]
    tasks[index] = task
    claims = copy.deepcopy(state.get("task_claims") or {})
    claims.pop(task["id"], None)
    return canonical_state.update_canonical_state(
        repo_root,
        {
            "tasks": tasks,
            "task_claims": claims,
            "verification": {
                "level": "evidence recorded",
                "evidence": task["evidence"],
                "stale": False,
            },
        },
        history_entry={
            "event": "task-completed",
            "status": "done",
            "task": task["id"],
            "claim_id": claim_id,
        },
    )


def build_subagent_assignment(
    *,
    task: str,
    user_requested: bool,
    codex_requires_subagent: bool,
    reason: str,
    max_parallel: int = 2,
) -> dict[str, Any]:
    if not user_requested:
        return {
            "approved": False,
            "reason": "explicit-user-request-required",
            "workflow_owner": "acc",
        }
    if not codex_requires_subagent:
        return {
            "approved": False,
            "reason": "codex-subagent-need-not-present",
            "workflow_owner": "acc",
        }
    return {
        "approved": True,
        "workflow_owner": "acc",
        "task": str(task).strip(),
        "reason": str(reason).strip(),
        "bounds": {
            "max_parallel": max(1, min(int(max_parallel), 4)),
            "return_to": "acc",
            "allowed_output": "concise evidence and result only",
            "durable_truth": False,
        },
    }


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="ACC task coordination CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    status = sub.add_parser("status")
    status.add_argument("--repo-root", default=".")

    claim = sub.add_parser("claim")
    claim.add_argument("--repo-root", default=".")
    claim.add_argument("--task-id", required=True)
    claim.add_argument("--owner", default="acc")
    claim.add_argument("--claim-id", default=None)

    release = sub.add_parser("release")
    release.add_argument("--repo-root", default=".")
    release.add_argument("--task-id", required=True)
    release.add_argument("--claim-id", required=True)

    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    if args.cmd == "status":
        state = canonical_state.read_canonical_state(root)
        print(json.dumps({
            "tasks": state.get("tasks", []),
            "task_claims": state.get("task_claims", {}),
        }, indent=2))
        return

    if args.cmd == "claim":
        try:
            result = claim_task(root, args.task_id, owner=args.owner, claim_id=args.claim_id)
        except TaskCoordinationError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"tasks": result.get("tasks", [])}, indent=2))
        return

    if args.cmd == "release":
        try:
            result = complete_task(root, args.task_id, claim_id=args.claim_id, evidence=[])
        except TaskCoordinationError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"tasks": result.get("tasks", [])}, indent=2))
        return


if __name__ == "__main__":
    main()
