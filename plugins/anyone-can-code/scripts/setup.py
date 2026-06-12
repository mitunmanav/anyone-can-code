#!/usr/bin/env python3
"""
Project setup for Anyone Can Code.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime_info


def plugin_root() -> Path:
    root = os.environ.get("PLUGIN_ROOT")
    if root:
        return Path(root)
    return Path(__file__).resolve().parent.parent


PLUGIN_ROOT = plugin_root()
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
REFERENCE = PLUGIN_ROOT / "reference" / "project"
HOOKS_DIR = PLUGIN_ROOT / "hooks"
DOCTOR = PLUGIN_ROOT / "scripts" / "doctor.py"
PROJECT_NAMESPACE = "anyone-can-code"

DEFAULT_PREFERENCES = {
    "schema_version": 2,
    "persona_mode": "builder",
    "persona_allowed_modes": ["builder", "developer", "mixed"],
    "verbosity": "simple",
    "automation_level": "assisted",
    "communication_mode": "caveman-strict",
    "automation_preference": "aggressive",
    "learning_preference": "enabled",
    "research_preference": "local-first",
    "approval_preference": "ask-for-secrets-paid-login-destructive-product",
    "plugin_routing": "automatic",
    "browser_preference": "ask",
    "learn_mode": "trigger-auto",
    "repo_mode": "unknown",
}


def plugin_version() -> str:
    if not MANIFEST.exists():
        return "0.0.0"
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8")).get("version", "0.0.0")
    except (json.JSONDecodeError, OSError):
        return "0.0.0"


def project_root(target: Path) -> Path:
    return target / ".codex" / PROJECT_NAMESPACE


def ensure_project_layout(target: Path) -> dict[str, Path]:
    root = project_root(target)
    paths = {
        "root": root,
        "state": root / "state",
        "artifacts": root / "artifacts",
        "learning": root / "learning",
        "logs": root / "logs",
        "backups": root / "backups",
        "settings": root / "settings",
        "migrations": root / "migrations",
        "hooks": target / ".codex" / "hooks",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def write_json_if_missing(path: Path, payload: dict, force: bool = False) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def merge_json_defaults(path: Path, defaults: dict, force: bool = False) -> None:
    if force or not path.exists():
        write_json_if_missing(path, defaults, force=True)
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(payload, dict):
        return
    changed = False
    for key, value in defaults.items():
        if key not in payload:
            payload[key] = value
            changed = True
    if changed:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text_if_missing(path: Path, text: str, force: bool = False) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_project_hooks(target: Path, force: bool = False) -> None:
    hooks_root = target / ".codex" / "hooks"
    hooks_root.mkdir(parents=True, exist_ok=True)
    source_hooks_json = REFERENCE / ".codex" / "hooks.json"
    source_scripts = HOOKS_DIR / "scripts"
    if source_hooks_json.exists():
        if force or not (hooks_root.parent / "hooks.json").exists():
            shutil.copy2(source_hooks_json, hooks_root.parent / "hooks.json")
    if source_scripts.exists():
        dest_scripts = hooks_root / "scripts"
        shutil.copytree(source_scripts, dest_scripts, dirs_exist_ok=True)


def bootstrap_project(target: Path, force: bool = False, install_project_hooks: bool = False) -> None:
    paths = ensure_project_layout(target)
    version = plugin_version()
    workflow_defaults = {
        "schema_version": 2,
        "phase": "idle",
        "route": "",
        "entry_mode": "",
        "active_goal": "",
        "active_spec": "",
        "last_task": "",
        "next_step": "",
        "last_verification": "",
        "persona_mode": DEFAULT_PREFERENCES["persona_mode"],
        "repo_mode": DEFAULT_PREFERENCES["repo_mode"],
        "setup_state": "ready",
        "communication_mode": DEFAULT_PREFERENCES["communication_mode"],
        "memory_mode": "mcp-first",
        "updated_at": "",
    }
    merge_json_defaults(paths["settings"] / "preferences.json", DEFAULT_PREFERENCES, force=force)
    merge_json_defaults(
        paths["state"] / "workflow.json",
        workflow_defaults,
        force=force,
    )
    write_json_if_missing(
        paths["state"] / "install.json",
        {
            "schema_version": 2,
            "plugin_version": version,
            "installed_via": "setup.py",
            "hook_mode": "project" if install_project_hooks else "bundled",
            "memory_mode": "mcp-first",
            "mcp_server": "memory",
        },
        force=True,
    )
    write_text_if_missing(
        target / "AGENTS.md",
        (REFERENCE / "AGENTS.md").read_text(encoding="utf-8"),
        force=force,
    )
    write_text_if_missing(
        paths["artifacts"] / "README.md",
        "# Anyone Can Code Artifacts\n\nThis folder stores resumable workflow artifacts such as plans, specs, resume notes, and verification records.\n",
        force=force,
    )
    write_text_if_missing(
        paths["learning"] / "README.md",
        "# Anyone Can Code Learning\n\nMain durable learning now lives in the bundled MCP memory server. Keep this folder tiny: short ledgers, fallback crumbs, and local recovery notes only.\n",
        force=force,
    )
    if install_project_hooks:
        copy_project_hooks(target, force=force)
    config_path = target / ".codex" / "config.toml"
    if not config_path.exists() or force:
        shutil.copy2(REFERENCE / ".codex" / "config.toml", config_path)


def run_doctor(target: Path) -> dict | None:
    if not DOCTOR.exists():
        return None
    env = os.environ.copy()
    env["ACC_PROJECT_ROOT"] = str(target)
    result = subprocess.run(
        [sys.executable, str(DOCTOR), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap Anyone Can Code project state")
    parser.add_argument("target", nargs="?", default=".", help="Project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite bootstrap files")
    parser.add_argument(
        "--project-hooks",
        action="store_true",
        help="Also install repo-local hooks.json and copied scripts under .codex/hooks/",
    )
    parser.add_argument("--check", action="store_true", help="Only run diagnostics")
    parser.add_argument("--version", action="store_true", help="Print plugin version and exit")
    args = parser.parse_args()

    if args.version:
        print(plugin_version())
        return

    target = Path(args.target).resolve()
    if args.check:
        result = run_doctor(target)
        print(json.dumps(result or {"error": "doctor.py not found"}, indent=2))
        return

    bootstrap_project(target, force=args.force, install_project_hooks=args.project_hooks)
    doctor = run_doctor(target)
    info = runtime_info.build_runtime_info(target, PLUGIN_ROOT)
    print(f"Setup done: {target}")
    print("Hooks:", "project" if args.project_hooks else "bundled")
    print("Memory: MCP first. Local tiny backup.")
    print("Dev mode: hooks off here. Test hooks by hand.")
    if info.get("marketplace_root"):
        print(f"Market: {info['marketplace_root']}")
    if info.get("plugin_source_root"):
        print(f"Source root: {info['plugin_source_root']}")
    if info.get("installed_plugin_root"):
        print(f"Runtime root: {info['installed_plugin_root']}")
    if doctor and "summary" in doctor:
        summary = doctor["summary"]
        print(f"Doctor: {summary['pass']} PASS, {summary['warn']} WARN, {summary['fail']} FAIL")
    print("Next: if plugin changed, restart Codex. Open new thread.")


if __name__ == "__main__":
    main()
