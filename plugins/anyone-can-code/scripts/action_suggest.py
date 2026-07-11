"""Suggest Codex app action buttons from the project type. Suggest only — the
user adds them in app Settings; ACC never writes app configuration."""

from __future__ import annotations

import json
from pathlib import Path


def suggest_actions(project_root: Path) -> list[dict]:
    actions: list[dict] = []
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except (OSError, json.JSONDecodeError):
            scripts = {}
        if "test" in scripts:
            actions.append({
                "name": "Run tests",
                "script": "npm test",
                "why": "One click checks the app still works.",
            })
        for key in ("dev", "start"):
            if key in scripts:
                actions.append({
                    "name": "Start app",
                    "script": f"npm run {key}" if key != "start" else "npm start",
                    "why": "One click starts the app so you can look at it.",
                })
                break

    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        if (project_root / "tests").is_dir():
            actions.append({
                "name": "Run tests",
                "script": "python -m pytest tests -q",
                "why": "One click checks the app still works.",
            })
        if (project_root / "manage.py").exists():
            actions.append({
                "name": "Start app",
                "script": "python manage.py runserver",
                "why": "One click starts the app so you can look at it.",
            })
    return actions
