"""First-run configuration: user type → auto-configure preferences."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

PREFS_SUBPATH = Path(".codex") / "anyone-can-code" / "settings" / "preferences.json"

# Modes: non-tech / middle / developer (aliases: builder / mixed / developer)
USER_TYPE_DEFAULTS: dict[str, dict[str, Any]] = {
    "builder": {
        "mode": "non-tech",
        "automation_preference": "aggressive",
        "learning_preference": "enabled",
        "communication_mode": "caveman-strict",
        "approval_preference": "minimal",
        "automations_opt_in": False,
        "knobs": {"plain": 3, "teach": 3, "tech_shown": 0, "questions": "life"},
    },
    "non-tech": {
        "mode": "non-tech",
        "automation_preference": "aggressive",
        "learning_preference": "enabled",
        "communication_mode": "caveman-strict",
        "approval_preference": "minimal",
        "automations_opt_in": False,
        "knobs": {"plain": 3, "teach": 3, "tech_shown": 0, "questions": "life"},
    },
    "developer": {
        "mode": "developer",
        "automation_preference": "balanced",
        "learning_preference": "enabled",
        "communication_mode": "caveman-strict",
        "approval_preference": "standard",
        "automations_opt_in": False,
        "knobs": {"plain": 1, "teach": 0, "tech_shown": 3, "questions": "tech"},
    },
    "mixed": {
        "mode": "middle",
        "automation_preference": "balanced",
        "learning_preference": "enabled",
        "communication_mode": "caveman-strict",
        "approval_preference": "standard",
        "automations_opt_in": False,
        "knobs": {"plain": 2, "teach": 1, "tech_shown": 1, "questions": "mixed"},
    },
    "middle": {
        "mode": "middle",
        "automation_preference": "balanced",
        "learning_preference": "enabled",
        "communication_mode": "caveman-strict",
        "approval_preference": "standard",
        "automations_opt_in": False,
        "knobs": {"plain": 2, "teach": 1, "tech_shown": 1, "questions": "mixed"},
    },
}


def _prefs_path(project_root: Path) -> Path:
    return project_root / PREFS_SUBPATH


def is_configured(project_root: Path) -> bool:
    path = _prefs_path(project_root)
    if not path.exists():
        return False
    try:
        prefs = json.loads(path.read_text(encoding="utf-8"))
        return bool(prefs.get("user_type"))
    except (json.JSONDecodeError, OSError):
        return False


def run_first_run(project_root: Path, user_type: str = "mixed") -> dict[str, Any]:
    """Configure ACC for first use. Idempotent — never overwrites existing user_type."""
    path = _prefs_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}

    if existing.get("user_type"):
        return {"configured": True, "user_type": existing["user_type"], "skipped": True}

    defaults = USER_TYPE_DEFAULTS.get(user_type, USER_TYPE_DEFAULTS["mixed"])
    merged = {**defaults, "user_type": user_type, **existing}
    path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return {"configured": True, "user_type": user_type}
