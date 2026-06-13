"""
Shared workflow state helpers for Anyone Can Code hooks.

Project-owned data lives in `.codex/anyone-can-code/`.
Plugin-owned writable data lives in `PLUGIN_DATA` when available.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


PROJECT_NAMESPACE = "anyone-can-code"
HOOK_DISABLE_MARKER = Path(".codex") / "anyone-can-code-hooks.disabled"

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


def read_state(repo_root: Path) -> dict:
    return _read_json(workflow_state_path(repo_root), DEFAULT_STATE)


def write_state(repo_root: Path, updates: dict) -> dict:
    current = read_state(repo_root)
    current.update(updates)
    current["updated_at"] = utc_now()
    _write_json(workflow_state_path(repo_root), current)
    return current


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
