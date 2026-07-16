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
# Plain words agents often use → real queue status. Never reject these.
TASK_STATUS_ALIASES = {
    "pending": "todo",
    "todo": "todo",
    "to-do": "todo",
    "to_do": "todo",
    "open": "todo",
    "new": "todo",
    "in_progress": "in_progress",
    "in-progress": "in_progress",
    "doing": "in_progress",
    "blocked": "blocked",
    "done": "done",
    "complete": "done",
    "completed": "done",
}


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
    raw_status = str(task.get("status") or task.get("state") or "todo").strip().lower()
    status = TASK_STATUS_ALIASES.get(raw_status, raw_status)
    if status not in TASK_STATUSES:
        raise TaskCoordinationError(f"Unsupported task status: {raw_status}")
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


def unclaim_task(
    repo_root: Path,
    task_id_or_name: str,
    *,
    claim_id: str | None = None,
    force: bool = False,
    reason: str = "helper-dead",
) -> dict[str, Any]:
    """Release a claim so another worker can take the job. Does NOT mark done.

    Item 45: if a helper died mid-task, free the claim. With force=True, clear
    any claim on the task (dead helper; claim_id may be unknown).
    """
    state = canonical_state.read_canonical_state(repo_root)
    tasks = [normalize_task(task) for task in state.get("tasks", [])]
    index = _find_task(tasks, task_id_or_name)
    task = copy.deepcopy(tasks[index])
    existing = str(task.get("claim_id") or "").strip()
    if task["status"] == "done":
        raise TaskCoordinationError("Done task cannot be unclaimed")
    if not existing and task["status"] != "in_progress":
        # already free
        return state
    if not force:
        if not claim_id:
            raise TaskCoordinationError("claim_id required unless force")
        if existing and existing != claim_id:
            raise TaskCoordinationError("Task claim mismatch")
    task.update(
        {
            "status": "todo",
            "claim_id": "",
            "claimed_by": "",
            "claimed_at": "",
            "owner": "acc",
        }
    )
    tasks[index] = task
    claims = copy.deepcopy(state.get("task_claims") or {})
    claims.pop(task["id"], None)
    active = state.get("active_task")
    updates: dict[str, Any] = {"tasks": tasks, "task_claims": claims}
    if active and str(active) in {task["id"], task["name"]}:
        updates["active_task"] = ""
    return canonical_state.update_canonical_state(
        repo_root,
        updates,
        history_entry={
            "event": "task-unclaimed",
            "status": "todo",
            "task": task["id"],
            "reason": str(reason or "helper-dead")[:120],
            "forced": bool(force),
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

    release = sub.add_parser("release", help="Unclaim task (not done) so another can take it")
    release.add_argument("--repo-root", default=".")
    release.add_argument("--task-id", required=True)
    release.add_argument("--claim-id", default=None)
    release.add_argument("--force", action="store_true", help="Clear claim even if claim_id unknown (dead helper)")
    release.add_argument("--reason", default="helper-dead")

    complete = sub.add_parser("complete", help="Mark task done with claim + evidence")
    complete.add_argument("--repo-root", default=".")
    complete.add_argument("--task-id", required=True)
    complete.add_argument("--claim-id", required=True)
    complete.add_argument("--evidence", action="append", default=[])

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
            result = unclaim_task(
                root,
                args.task_id,
                claim_id=args.claim_id,
                force=bool(args.force),
                reason=args.reason,
            )
        except TaskCoordinationError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"tasks": result.get("tasks", []), "task_claims": result.get("task_claims", {})}, indent=2))
        return

    if args.cmd == "complete":
        try:
            result = complete_task(
                root,
                args.task_id,
                claim_id=args.claim_id,
                evidence=list(args.evidence or []),
            )
        except TaskCoordinationError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"tasks": result.get("tasks", [])}, indent=2))
        return


if __name__ == "__main__":
    main()
