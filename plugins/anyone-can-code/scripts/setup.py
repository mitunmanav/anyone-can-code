#!/usr/bin/env python3
"""
Project setup for Anyone Can Code.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import quote

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
OBSIDIAN_DOWNLOAD_URL = "https://obsidian.md/download"
VIEWER_MODES = {"none", "obsidian"}
VIEWER_ACTIONS = {"none", "download-page", "install", "open-vault"}
IMPORT_SCOPES = {"project", "user", "shared"}
IMPORT_SCOPE_CHOICES = {"ask", *IMPORT_SCOPES}

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
    "memory_path": ".codex/anyone-can-code/memory/notes",
    "memory_mode": "portable-markdown",
    "viewer_mode": "none",
    "import_sources": [],
    "import_scope": "ask",
    "production_repo_caution": True,
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


def resolve_memory_notes_path(target: Path, memory_path: Path | str | None) -> Path:
    selected = Path(memory_path or DEFAULT_PREFERENCES["memory_path"]).expanduser()
    if not selected.is_absolute():
        selected = target / selected
    return selected.absolute()


def ensure_memory_layout(notes_path: Path) -> None:
    for name in ("project", "user", "shared", "lessons", "failures", "decisions", "evidence", "archive"):
        (notes_path / name).mkdir(parents=True, exist_ok=True)
    (notes_path.parent / "index").mkdir(parents=True, exist_ok=True)
    (notes_path.parent / "imports").mkdir(parents=True, exist_ok=True)


def detect_obsidian() -> Path | None:
    command = shutil.which("Obsidian") or shutil.which("Obsidian.exe")
    if command:
        return Path(command)
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidian" / "Obsidian.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Obsidian" / "Obsidian.exe",
    ]
    return next((path for path in candidates if str(path.parent) != "." and path.exists()), None)


def run_viewer_action(
    viewer_mode: str,
    viewer_action: str,
    consent: bool,
    notes_path: Path,
) -> dict:
    detected = detect_obsidian()
    result = {
        "mode": viewer_mode,
        "action": viewer_action,
        "detected": bool(detected),
        "detected_path": str(detected) if detected else "",
        "status": "not requested",
        "instructions": "",
    }
    if viewer_mode == "none" or viewer_action == "none":
        return result
    if viewer_mode not in VIEWER_MODES:
        raise ValueError(f"Unsupported viewer mode: {viewer_mode}")
    if viewer_action not in VIEWER_ACTIONS:
        raise ValueError(f"Unsupported viewer action: {viewer_action}")
    if not consent:
        raise ValueError("Viewer action requires explicit consent")

    if viewer_action == "download-page":
        opened = webbrowser.open(OBSIDIAN_DOWNLOAD_URL)
        result["status"] = "official download page opened" if opened else "download page could not open"
        result["instructions"] = OBSIDIAN_DOWNLOAD_URL
        return result

    if viewer_action == "install":
        winget = shutil.which("winget")
        if not winget:
            result["status"] = "install unavailable"
            result["instructions"] = f"Open official download page: {OBSIDIAN_DOWNLOAD_URL}"
            return result
        completed = subprocess.run(
            [winget, "install", "--id", "Obsidian.Obsidian", "--exact", "--source", "winget"],
            check=False,
            text=True,
            capture_output=True,
        )
        result["status"] = (
            "install command completed" if completed.returncode == 0 else "install command failed"
        )
        result["exit_code"] = completed.returncode
        return result

    vault_uri = f"obsidian://open?path={quote(str(notes_path))}"
    opened = webbrowser.open(vault_uri)
    result["status"] = "vault open requested" if opened else "automatic vault open unavailable"
    result["instructions"] = (
        f'In Obsidian choose "Open folder as vault", then select: {notes_path}'
    )
    return result


def load_memory_server():
    path = PLUGIN_ROOT / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("acc_setup_memory_server", path)
    if not spec or not spec.loader:
        raise RuntimeError("Memory server could not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_session_import(
    target: Path,
    notes_path: Path,
    sources: list[Path],
    scope: str,
    confirmed: bool,
) -> dict:
    selected = [str(path.expanduser().resolve()) for path in sources]
    result = {
        "status": "not requested" if not selected else "preview only",
        "scope": scope,
        "selected_paths": selected,
        "imported": 0,
        "receipt_path": "",
    }
    if not selected or not confirmed:
        return result
    if scope not in IMPORT_SCOPES:
        raise ValueError(f"Unsupported import scope: {scope}")
    old_root = os.environ.get("ACC_MCP_DATA_ROOT")
    os.environ["ACC_MCP_DATA_ROOT"] = str(notes_path.parent)
    try:
        receipt = load_memory_server().import_session_files(
            {
                "paths": selected,
                "scope": scope,
                "project_root": str(target),
                "dry_run": False,
            }
        )
    finally:
        if old_root is None:
            os.environ.pop("ACC_MCP_DATA_ROOT", None)
        else:
            os.environ["ACC_MCP_DATA_ROOT"] = old_root
    result.update(
        {
            "status": "completed" if receipt.get("status") == "verified" else "rolled back",
            "imported": receipt["imported_count"],
            "receipt_path": receipt.get("receipt_path") or receipt.get("rollback_receipt_path", ""),
        }
    )
    return result


def write_setup_receipt(target: Path, notes_path: Path, receipt: dict) -> dict:
    receipt_id = f"setup-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    receipt_dir = project_root(target) / "state" / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    json_path = receipt_dir / f"{receipt_id}.json"
    markdown_path = receipt_dir / f"{receipt_id}.md"
    receipt["receipt_id"] = receipt_id
    receipt["receipt_json"] = str(json_path)
    receipt["receipt_markdown"] = str(markdown_path)
    json_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    imports = receipt["imports"]
    viewer = receipt["viewer"]
    markdown_path.write_text(
        "\n".join(
            [
                "# Anyone Can Code Setup Receipt",
                "",
                f"- Memory: portable Markdown",
                f"- Storage: `{notes_path}`",
                f"- Viewer: `{viewer['mode']}`",
                f"- Viewer action: `{viewer['action']}`",
                f"- Viewer result: {viewer['status']}",
                f"- Import result: {imports['status']}",
                f"- Import scope: `{imports['scope']}`",
                f"- Selected import paths: {len(imports['selected_paths'])}",
                f"- Imported notes: {imports['imported']}",
                f"- Import receipt: {imports['receipt_path'] or 'none'}",
                "- Files moved or deleted: no",
                "- Registry changed: no",
                "- Third-party agreements auto-accepted: no",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return receipt


def ensure_project_layout(target: Path) -> dict[str, Path]:
    root = project_root(target)
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


def bootstrap_project(
    target: Path,
    force: bool = False,
    install_project_hooks: bool = False,
    memory_path: Path | str | None = None,
    viewer_mode: str = "none",
    viewer_action: str = "none",
    consent_viewer_action: bool = False,
    import_sources: list[Path] | None = None,
    import_scope: str = "ask",
    confirm_import: bool = False,
) -> dict:
    if viewer_mode not in VIEWER_MODES:
        raise ValueError(f"Unsupported viewer mode: {viewer_mode}")
    if viewer_action not in VIEWER_ACTIONS:
        raise ValueError(f"Unsupported viewer action: {viewer_action}")
    if import_scope not in IMPORT_SCOPE_CHOICES:
        raise ValueError(f"Unsupported import scope: {import_scope}")
    if viewer_action != "none" and viewer_mode != "obsidian":
        raise ValueError("Viewer actions require viewer mode 'obsidian'")
    if viewer_action != "none" and not consent_viewer_action:
        raise ValueError("Viewer action requires explicit consent")
    if confirm_import and import_scope not in IMPORT_SCOPES:
        raise ValueError("Confirmed import requires project, user, or shared scope")
    paths = ensure_project_layout(target)
    notes_path = resolve_memory_notes_path(target, memory_path)
    ensure_memory_layout(notes_path)
    version = plugin_version()
    selected_memory_path = (
        DEFAULT_PREFERENCES["memory_path"]
        if memory_path is None
        else str(notes_path)
    )
    selected_preferences = {
        **DEFAULT_PREFERENCES,
        "memory_path": selected_memory_path,
        "viewer_mode": viewer_mode,
        "import_sources": [str(path.expanduser().resolve()) for path in (import_sources or [])],
        "import_scope": import_scope,
    }
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
        "persona_mode": DEFAULT_PREFERENCES["persona_mode"],
        "repo_mode": DEFAULT_PREFERENCES["repo_mode"],
        "setup_state": "ready",
        "communication_mode": DEFAULT_PREFERENCES["communication_mode"],
        "memory_mode": DEFAULT_PREFERENCES["memory_mode"],
        "viewer_mode": viewer_mode,
        "updated_at": "",
    }
    merge_json_defaults(paths["settings"] / "preferences.json", selected_preferences, force=force)
    preferences_path = paths["settings"] / "preferences.json"
    preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
    preferences.update(
        {
            "memory_path": selected_memory_path,
            "memory_mode": "portable-markdown",
            "viewer_mode": viewer_mode,
            "import_sources": selected_preferences["import_sources"],
            "import_scope": import_scope,
        }
    )
    preferences_path.write_text(json.dumps(preferences, indent=2) + "\n", encoding="utf-8")
    merge_json_defaults(
        paths["state"] / "workflow.json",
        workflow_defaults,
        force=force,
    )
    workflow_path = paths["state"] / "workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow.update({"memory_mode": "portable-markdown", "viewer_mode": viewer_mode})
    workflow_path.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
    write_json_if_missing(
        paths["state"] / "install.json",
        {
            "schema_version": 2,
            "plugin_version": version,
            "installed_via": "setup.py",
            "hook_mode": "project" if install_project_hooks else "bundled",
            "memory_mode": DEFAULT_PREFERENCES["memory_mode"],
            "memory_path": selected_memory_path,
            "viewer_mode": viewer_mode,
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
        "# Anyone Can Code Learning\n\nDurable learning belongs in portable linked Markdown memory. Keep this folder tiny: short ledgers, fallback crumbs, and local recovery notes only.\n",
        force=force,
    )
    write_text_if_missing(
        paths["memory"] / "README.md",
        "# Anyone Can Code Memory\n\nSource of truth is linked Markdown under `notes/`. `index/` is rebuildable. `imports/` stores source backups, snapshots, transaction recovery data, and success or rollback receipts. Legacy JSONL remains migration input only. Viewer is optional.\n",
        force=force,
    )
    if install_project_hooks:
        copy_project_hooks(target, force=force)
    config_path = target / ".codex" / "config.toml"
    if not config_path.exists() or force:
        shutil.copy2(REFERENCE / ".codex" / "config.toml", config_path)
    viewer = run_viewer_action(
        viewer_mode,
        viewer_action,
        consent_viewer_action,
        notes_path,
    )
    imports = run_session_import(
        target,
        notes_path,
        import_sources or [],
        import_scope,
        confirm_import,
    )
    return write_setup_receipt(
        target,
        notes_path,
        {
            "memory_mode": "portable-markdown",
            "memory_path": str(notes_path),
            "viewer": viewer,
            "imports": imports,
            "project_hooks": install_project_hooks,
            "hidden_actions": [],
        },
    )


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
    parser.add_argument(
        "--memory-path",
        help="Linked-Markdown notes folder. Default: .codex/anyone-can-code/memory/notes",
    )
    parser.add_argument("--viewer", choices=sorted(VIEWER_MODES), default="none")
    parser.add_argument("--viewer-action", choices=sorted(VIEWER_ACTIONS), default="none")
    parser.add_argument(
        "--consent-viewer-action",
        action="store_true",
        help="Confirm requested viewer download, install, launch, or vault-open action",
    )
    parser.add_argument(
        "--import-source",
        action="append",
        default=[],
        help="Exact session file or folder selected by user; repeat for multiple paths",
    )
    parser.add_argument("--import-scope", choices=sorted(IMPORT_SCOPE_CHOICES), default="ask")
    parser.add_argument(
        "--confirm-import",
        action="store_true",
        help="Import selected sources now. Without this flag setup shows preview only.",
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

    receipt = bootstrap_project(
        target,
        force=args.force,
        install_project_hooks=args.project_hooks,
        memory_path=args.memory_path,
        viewer_mode=args.viewer,
        viewer_action=args.viewer_action,
        consent_viewer_action=args.consent_viewer_action,
        import_sources=[Path(value) for value in args.import_source],
        import_scope=args.import_scope,
        confirm_import=args.confirm_import,
    )
    doctor = run_doctor(target)
    info = runtime_info.build_runtime_info(target, PLUGIN_ROOT)
    print(f"Setup done: {target}")
    print("Hooks:", "project" if args.project_hooks else "bundled")
    print(f"Memory: portable Markdown at {receipt['memory_path']}")
    print(f"Viewer: {receipt['viewer']['mode']}. {receipt['viewer']['status']}.")
    print(
        f"Imports: {receipt['imports']['status']}; "
        f"scope {receipt['imports']['scope']}; "
        f"selected {len(receipt['imports']['selected_paths'])}; "
        f"imported {receipt['imports']['imported']}."
    )
    if receipt["viewer"]["instructions"]:
        print(f"Viewer instructions: {receipt['viewer']['instructions']}")
    print(f"Receipt: {receipt['receipt_markdown']}")
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
