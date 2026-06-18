"""
Shared workflow state helpers for Anyone Can Code hooks.

Project-owned data lives in `.codex/anyone-can-code/`.
Plugin-owned writable data lives in `PLUGIN_DATA` when available.
"""

from __future__ import annotations

import json
import hashlib
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Callable

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import canonical_state


PROJECT_NAMESPACE = "anyone-can-code"
HOOK_DISABLE_MARKER = Path(".codex") / "anyone-can-code-hooks.disabled"
HOOK_RETRY_LIMIT = 2
PROJECT_SCAN_MAX_DEPTH = 3
PROJECT_SCAN_EXCLUDED_DIRS = {
    ".codex",
    ".flow",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
}
HOOK_PURPOSES = {
    "guard": "Block obvious prompt-injection and dangerous command signals.",
    "audit": "Measure tool-use signals for later evidence review.",
    "load_session": "Inject small resumable context at session start.",
    "save_session": "Save small resumable context and learning signals.",
}

DEFAULT_STATE = {
    "schema_version": 2,
    "phase": "idle",
    "route": "",
    "entry_mode": "",
    "active_goal": "",
    "active_spec": "",
    "last_task": "",
    "next_step": "",
    "last_verification": "",
    "states": {
        "build": "in scope",
        "tests": "in scope",
        "deploy": "deferred",
    },
    "status_line": "Status: build in scope, tests in scope, deploy deferred",
    "work_state": "in scope",
    "verification_state": "in scope",
    "evidence": [],
    "failures": [],
    "silent_failures": [],
    "unverified": ["build", "tests"],
    "uncertainty": [],
    "communication_mode": "caveman-strict",
    "memory_mode": "portable-markdown",
    "viewer_mode": "none",
    "updated_at": "",
}

DEFAULT_PREFERENCES = {
    "schema_version": 2,
    "communication_mode": "caveman-strict",
    "automation_preference": "aggressive",
    "learning_preference": "enabled",
    "browser_preference": "ask",
    "learn_mode": "trigger-auto",
    "memory_path": ".codex/anyone-can-code/memory/notes",
    "memory_mode": "portable-markdown",
    "viewer_mode": "none",
    "import_sources": [],
    "import_scope": "ask",
    "production_repo_caution": True,
}


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def acc_hooks_disabled(location: Path) -> bool:
    current = location.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        try:
            if (candidate / HOOK_DISABLE_MARKER).is_file():
                return True
        except OSError:
            continue
    return False


def plugin_runtime_root(script_path: Path) -> Path:
    plugin_data = os.environ.get("PLUGIN_DATA")
    if plugin_data:
        return Path(plugin_data)
    return script_path.resolve().parent.parent / ".runtime"


def project_root(repo_root: Path) -> Path:
    return repo_root / ".codex" / PROJECT_NAMESPACE


def ensure_project_layout(repo_root: Path) -> dict[str, Path]:
    root = project_root(repo_root)
    paths = {
        "root": root,
        "state": root / "state",
        "artifacts": root / "artifacts",
        "learning": root / "learning",
        "memory": root / "memory",
        "memory_notes": root / "memory" / "notes",
        "memory_project": root / "memory" / "notes" / "project",
        "memory_user": root / "memory" / "notes" / "user",
        "memory_shared": root / "memory" / "notes" / "shared",
        "memory_lessons": root / "memory" / "notes" / "lessons",
        "memory_failures": root / "memory" / "notes" / "failures",
        "memory_decisions": root / "memory" / "notes" / "decisions",
        "memory_evidence": root / "memory" / "notes" / "evidence",
        "memory_archive": root / "memory" / "notes" / "archive",
        "memory_index": root / "memory" / "index",
        "memory_imports": root / "memory" / "imports",
        "logs": root / "logs",
        "backups": root / "backups",
        "settings": root / "settings",
        "migrations": root / "migrations",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def workflow_state_path(repo_root: Path) -> Path:
    return ensure_project_layout(repo_root)["state"] / "workflow.json"


def preferences_path(repo_root: Path) -> Path:
    return ensure_project_layout(repo_root)["settings"] / "preferences.json"


def journal_path(repo_root: Path, name: str) -> Path:
    return ensure_project_layout(repo_root)["logs"] / name


def signal_log_path(repo_root: Path) -> Path:
    return journal_path(repo_root, "signal-ledger.jsonl")


def mistake_log_path(repo_root: Path) -> Path:
    return journal_path(repo_root, "mistake-ledger.jsonl")


def hook_health_path(repo_root: Path) -> Path:
    return journal_path(repo_root, "hook-health.json")


def hook_health_ledger_path(repo_root: Path) -> Path:
    return journal_path(repo_root, "hook-health-ledger.jsonl")


def _read_json(path: Path, default: dict) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return dict(default)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_hook_health(repo_root: Path) -> dict:
    health = _read_json(
        hook_health_path(repo_root),
        {
            "schema_version": 1,
            "retry_limit": HOOK_RETRY_LIMIT,
            "hooks": {},
        },
    )
    health.setdefault("schema_version", 1)
    health.setdefault("retry_limit", HOOK_RETRY_LIMIT)
    health.setdefault("hooks", {})
    return health


def hook_circuit_open(repo_root: Path, hook_name: str) -> bool:
    entry = read_hook_health(repo_root).get("hooks", {}).get(hook_name, {})
    return bool(entry.get("circuit_open"))


def record_hook_result(
    repo_root: Path,
    hook_name: str,
    status: str,
    *,
    reason: str = "",
    duration_ms: int = 0,
) -> dict:
    health = read_hook_health(repo_root)
    hooks = health.setdefault("hooks", {})
    previous = hooks.get(hook_name, {})
    failures = int(previous.get("consecutive_failures") or 0)
    if status == "pass":
        failures = 0
    elif status == "fail":
        failures += 1
    circuit_open = failures >= HOOK_RETRY_LIMIT
    entry = {
        "purpose": HOOK_PURPOSES.get(hook_name, "Optional helper signal."),
        "status": status,
        "reason": reason[:240],
        "checked_at": utc_now(),
        "duration_ms": duration_ms,
        "consecutive_failures": failures,
        "retry_limit": HOOK_RETRY_LIMIT,
        "circuit_open": circuit_open,
    }
    hooks[hook_name] = entry
    _write_json(hook_health_path(repo_root), health)
    append_jsonl(
        hook_health_ledger_path(repo_root),
        {
            "timestamp": entry["checked_at"],
            "hook": hook_name,
            "purpose": entry["purpose"],
            "status": status,
            "reason": entry["reason"],
            "duration_ms": duration_ms,
            "circuit_open": circuit_open,
        },
    )
    return entry


def run_optional_hook(repo_root: Path, hook_name: str, worker: Callable[[], dict]) -> dict:
    if hook_circuit_open(repo_root, hook_name):
        record_hook_result(repo_root, hook_name, "skipped", reason="circuit-open")
        return {}
    started = time.monotonic()
    try:
        result = worker()
    except Exception as exc:  # pragma: no cover - hook best effort
        duration_ms = int((time.monotonic() - started) * 1000)
        record_hook_result(repo_root, hook_name, "fail", reason=str(exc), duration_ms=duration_ms)
        return {}
    duration_ms = int((time.monotonic() - started) * 1000)
    record_hook_result(repo_root, hook_name, "pass", duration_ms=duration_ms)
    return result


def read_state(repo_root: Path) -> dict:
    return _read_json(workflow_state_path(repo_root), DEFAULT_STATE)


def write_state(repo_root: Path, updates: dict) -> dict:
    normalized = dict(updates)
    if "last_task" in normalized and "active_task" not in normalized:
        normalized["active_task"] = normalized["last_task"]
    if "next_step" in normalized and "next_action" not in normalized:
        normalized["next_action"] = normalized["next_step"]
    return canonical_state.update_canonical_state(repo_root, normalized)


def read_preferences(repo_root: Path) -> dict:
    return _read_json(preferences_path(repo_root), DEFAULT_PREFERENCES)


def write_preferences(repo_root: Path, updates: dict) -> dict:
    current = read_preferences(repo_root)
    current.update(updates)
    _write_json(preferences_path(repo_root), current)
    return current


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def read_recent_jsonl(path: Path, limit: int = 25) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def hook_start_location(payload: dict) -> Path:
    raw = payload.get("cwd") or payload.get("workspace_root") or os.getcwd()
    try:
        location = Path(str(raw)).expanduser().resolve()
    except OSError:
        location = Path.cwd().resolve()
    return location.parent if location.is_file() else location


def git_root_from_ancestors(location: Path) -> Path | None:
    current = location.resolve()
    for candidate in (current, *current.parents):
        try:
            if (candidate / ".git").exists():
                return candidate
        except OSError:
            continue
    return None


def is_hook_project_candidate(path: Path) -> bool:
    try:
        return (path / ".git").exists() or (path / ".codex" / PROJECT_NAMESPACE).exists()
    except OSError:
        return False


def is_meaningful_hook_project(path: Path) -> bool:
    try:
        return (path / ".codex" / PROJECT_NAMESPACE).exists()
    except OSError:
        return False


def discover_nested_hook_projects(location: Path) -> list[Path]:
    discovered: list[Path] = []
    seen: set[Path] = set()
    pending: list[tuple[Path, int]] = [(location.resolve(), 0)]
    while pending:
        current, depth = pending.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if is_hook_project_candidate(current):
            discovered.append(current)
            continue
        if depth >= PROJECT_SCAN_MAX_DEPTH:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            continue
        for child in children:
            if (
                not child.is_dir()
                or child.is_symlink()
                or child.name in PROJECT_SCAN_EXCLUDED_DIRS
            ):
                continue
            try:
                pending.append((child.resolve(), depth + 1))
            except OSError:
                continue
    return discovered


def resolve_hook_project(payload: dict) -> dict:
    location = hook_start_location(payload)
    if acc_hooks_disabled(location):
        return {
            "status": "disabled",
            "reason": "acc-hooks-disabled",
            "cwd": str(location),
            "fallback_root": str(location),
            "candidates": [],
        }

    direct = git_root_from_ancestors(location)
    candidates = [direct] if direct is not None else discover_nested_hook_projects(location)
    candidates = list(dict.fromkeys(candidate.resolve() for candidate in candidates))
    meaningful = [candidate for candidate in candidates if is_meaningful_hook_project(candidate)]
    selectable = meaningful or candidates

    if len(selectable) == 1:
        chosen = selectable[0]
        if acc_hooks_disabled(chosen):
            return {
                "status": "disabled",
                "reason": "acc-hooks-disabled",
                "cwd": str(location),
                "fallback_root": str(location),
                "candidates": [str(candidate) for candidate in candidates],
            }
        return {
            "status": "resolved",
            "reason": "single-project",
            "cwd": str(location),
            "fallback_root": str(location),
            "project_root": str(chosen),
            "candidates": [str(candidate) for candidate in candidates],
        }
    if len(selectable) > 1:
        return {
            "status": "ambiguous",
            "reason": "ambiguous-project",
            "cwd": str(location),
            "fallback_root": str(location),
            "candidates": [str(candidate) for candidate in selectable],
        }
    return {
        "status": "unresolved",
        "reason": "no-project",
        "cwd": str(location),
        "fallback_root": str(location),
        "candidates": [],
    }


def hook_receipt_path(root: Path) -> Path:
    return ensure_project_layout(root)["logs"] / "hook-receipts.jsonl"


def digest_payload(value: object) -> str:
    try:
        text = json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        text = str(value)
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def hook_output_kind(result: dict) -> str:
    if not result:
        return "empty"
    specific = result.get("hookSpecificOutput") if isinstance(result, dict) else None
    if isinstance(specific, dict):
        if specific.get("additionalContext"):
            return "context"
        if specific.get("permissionDecision") or specific.get("decision"):
            return "permission"
        return "hookSpecificOutput"
    if result.get("decision"):
        return "decision"
    return "output"


def declared_state_writes(hook_name: str, event: str, result: dict) -> list[str]:
    if hook_name == "save_session":
        return [
            ".codex/anyone-can-code/state/workflow.json",
            ".codex/anyone-can-code/state/turn-ledger.jsonl",
            ".codex/anyone-can-code/state/session-snapshot.md",
            ".codex/anyone-can-code/artifacts/resume-note.md",
        ]
    if not result:
        return []
    if hook_name == "guard" and event == "UserPromptSubmit":
        return [
            ".codex/anyone-can-code/logs/signal-ledger.jsonl",
        ]
    if hook_name == "guard" and event == "PreToolUse":
        return [".codex/anyone-can-code/logs/blocked-events.jsonl"]
    if hook_name == "audit":
        return [
            ".codex/anyone-can-code/logs/tool-usage.jsonl",
            ".codex/anyone-can-code/logs/signal-ledger.jsonl",
        ]
    return []


def receipt_root_from_resolution(resolution: dict) -> Path | None:
    if resolution.get("status") == "disabled":
        return None
    root = resolution.get("project_root") or resolution.get("fallback_root") or resolution.get("cwd")
    return Path(str(root)).resolve() if root else None


def write_hook_receipt(root: Path, receipt: dict) -> None:
    append_jsonl(hook_receipt_path(root), receipt)


def run_hook_attempt(
    resolution: dict,
    hook_name: str,
    payload: dict,
    worker: Callable[[], dict],
) -> dict:
    if resolution.get("status") == "disabled":
        return {}

    receipt_root = receipt_root_from_resolution(resolution)
    if receipt_root is None:
        return {}

    started_at = utc_now()
    started = time.monotonic()
    result: dict = {}
    failure_class = ""
    skip_reason = ""
    status = str(resolution.get("status") or "unresolved")
    project_root_value = (
        resolution.get("project_root")
        or resolution.get("fallback_root")
        or resolution.get("cwd")
    )
    if project_root_value and "project_root" not in resolution:
        resolution["project_root"] = str(project_root_value)

    if hook_circuit_open(Path(str(project_root_value)), hook_name):
        skip_reason = "circuit-open"
        record_hook_result(Path(str(project_root_value)), hook_name, "skipped", reason=skip_reason)
    else:
        try:
            result = worker()
        except Exception as exc:  # pragma: no cover - hook best effort
            failure_class = exc.__class__.__name__
            result = {}
            record_hook_result(
                Path(str(project_root_value)),
                hook_name,
                "fail",
                reason=str(exc),
            )
        else:
            record_hook_result(Path(str(project_root_value)), hook_name, "pass")

    duration_ms = int((time.monotonic() - started) * 1000)
    output_kind = hook_output_kind(result)
    context_returned = output_kind == "context"
    state_write_paths = declared_state_writes(hook_name, str(payload.get("hook_event_name") or ""), result)
    if failure_class:
        final_effectiveness = "failed"
    elif skip_reason:
        final_effectiveness = "skipped"
    elif output_kind == "empty" and state_write_paths:
        final_effectiveness = "useful"
    elif output_kind == "empty":
        final_effectiveness = "no-op"
    else:
        final_effectiveness = "useful"

    event = str(payload.get("hook_event_name") or "")
    receipt = {
        "schema_version": 1,
        "correlation_id": str(
            payload.get("hook_run_id")
            or payload.get("run_id")
            or payload.get("tool_use_id")
            or f"acc-{uuid.uuid4().hex}"
        ),
        "session_id": str(payload.get("session_id") or ""),
        "turn_id": str(payload.get("turn_id") or ""),
        "hook": hook_name,
        "hook_event": event,
        "source": str(payload.get("source") or ""),
        "launcher_started_at": started_at,
        "script_entered_at": started_at,
        "completed_at": utc_now(),
        "duration_ms": duration_ms,
        "cwd": str(resolution.get("cwd") or ""),
        "resolver_candidates": list(resolution.get("candidates") or []),
        "chosen_project": str(project_root_value or ""),
        "resolution_state": status,
        "output_kind": output_kind,
        "output_digest": digest_payload(result),
        "context_returned": context_returned,
        "state_write_paths": state_write_paths,
        "state_write_result": "declared" if state_write_paths else "none",
        "skip_reason": skip_reason,
        "failure_class": failure_class,
        "exit_status": "success" if not failure_class else "failure",
        "circuit_state": "open" if skip_reason == "circuit-open" else "closed",
        "final_effectiveness": final_effectiveness,
    }
    write_hook_receipt(receipt_root, receipt)
    return result


def detect_phase(prompt: str) -> tuple[str | None, str | None]:
    prompt_lower = prompt.lower()
    mappings = [
        ("settings", "settings"),
        ("resume", "resume"),
        ("status", "status"),
        ("verify", "verify"),
        ("update", "update"),
        ("learn", "learn"),
        ("clarify", "clarify"),
        ("plan", "plan"),
        ("execute", "execute"),
        ("setup", "setup"),
        ("onboard", "onboard"),
    ]
    for keyword, phase in mappings:
        if f"${keyword}" in prompt_lower or f"/{keyword}" in prompt_lower or keyword in prompt_lower:
            return phase, keyword
    return detect_entry_mode(prompt), None


def detect_entry_mode(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(token in prompt_lower for token in ["bug", "broken", "failing", "error", "fix"]):
        return "bug-fix"
    if any(token in prompt_lower for token in ["review", "polish", "optimize", "clean up"]):
        return "polish-review"
    if any(token in prompt_lower for token in ["ship", "release", "deploy", "ready to go live"]):
        return "ship-verify"
    if any(token in prompt_lower for token in ["existing repo", "existing codebase", "in this repo", "current repo"]):
        return "existing-repo"
    if any(token in prompt_lower for token in ["spec", "requirements", "acceptance criteria"]):
        return "written-spec"
    if any(token in prompt_lower for token in ["feature", "add ", "implement ", "build this"]):
        return "feature-request"
    if any(token in prompt_lower for token in ["idea", "thinking", "brainstorm", "rough"]):
        return "idea"
    return "partial-idea"


def classify_uncertainty(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(token in prompt_lower for token in ["not sure", "maybe", "either", "decide for me", "whatever works"]):
        return "medium"
    if any(token in prompt_lower for token in ["unknown", "unclear", "depends", "need to confirm"]):
        return "high"
    return "low"
