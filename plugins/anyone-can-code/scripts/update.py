#!/usr/bin/env python3
"""
Project update helper for Anyone Can Code.
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
SETUP = PLUGIN_ROOT / "scripts" / "setup.py"
DOCTOR = PLUGIN_ROOT / "scripts" / "doctor.py"
PROJECT_NAMESPACE = "anyone-can-code"


def plugin_version() -> str:
    if not MANIFEST.exists():
        return "0.0.0"
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8")).get("version", "0.0.0")
    except (json.JSONDecodeError, OSError):
        return "0.0.0"


def project_root(target: Path) -> Path:
    return target / ".codex" / PROJECT_NAMESPACE


def install_state_path(target: Path) -> Path:
    return project_root(target) / "state" / "install.json"


def load_install_state(target: Path) -> dict:
    path = install_state_path(target)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema_version": 2,
        "plugin_version": "0.0.0",
        "hook_mode": "bundled",
        "memory_mode": "portable-markdown",
        "memory_path": ".codex/anyone-can-code/memory/notes",
        "viewer_mode": "none",
        "mcp_server": "memory",
    }


def backup_dir(target: Path, previous_version: str) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S")
    return project_root(target) / "backups" / f"pre-migrate-{previous_version}-{stamp}"


def copy_if_exists(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)


def backup_supported_data(target: Path, destination: Path) -> None:
    sources = [
        project_root(target) / "state",
        project_root(target) / "artifacts",
        project_root(target) / "learning",
        project_root(target) / "memory",
        project_root(target) / "settings",
        project_root(target) / "logs",
        target / "AGENTS.md",
        target / ".codex" / "config.toml",
    ]
    for source in sources:
        if source.exists():
            copy_if_exists(source, destination / source.relative_to(target))


def quarantine_corrupt_files(target: Path) -> list[str]:
    quarantined = []
    workflow_path = project_root(target) / "state" / "workflow.json"
    if workflow_path.exists():
        try:
            json.loads(workflow_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            quarantine = project_root(target) / "migrations" / "quarantine"
            quarantine.mkdir(parents=True, exist_ok=True)
            destination = quarantine / f"workflow-corrupt-{time.strftime('%Y%m%dT%H%M%S')}.json"
            shutil.move(str(workflow_path), str(destination))
            quarantined.append(str(destination))
    return quarantined


def write_migration_journal(
    target: Path,
    before_version: str,
    after_version: str,
    quarantined: list[str],
    memory_receipt: dict,
) -> Path:
    journal_dir = project_root(target) / "migrations"
    journal_dir.mkdir(parents=True, exist_ok=True)
    journal = journal_dir / f"migration-{time.strftime('%Y%m%dT%H%M%S')}.json"
    journal.write_text(
        json.dumps(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "before_version": before_version,
                "after_version": after_version,
                "quarantined": quarantined,
                "memory_migration": {
                    "status": memory_receipt.get("status"),
                    "sources": memory_receipt.get("sources", []),
                    "imported_count": memory_receipt.get("imported_count", 0),
                    "skipped_count": memory_receipt.get("skipped_count", 0),
                    "receipt_path": memory_receipt.get("receipt_path", ""),
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return journal


def run_setup(target: Path, hook_mode: str, before: dict) -> None:
    args = [sys.executable, str(SETUP), str(target), "--force"]
    if hook_mode == "project":
        args.append("--project-hooks")
    memory_path = before.get("memory_path")
    if memory_path:
        args.extend(["--memory-path", str(memory_path)])
    viewer_mode = before.get("viewer_mode", "none")
    if viewer_mode in {"none", "obsidian"}:
        args.extend(["--viewer", viewer_mode])
    subprocess.run(args, check=True, timeout=30)


def load_memory_server():
    path = PLUGIN_ROOT / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("acc_update_memory_server", path)
    if not spec or not spec.loader:
        raise RuntimeError("Memory server could not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_memory_sources(target: Path) -> list[Path]:
    root = project_root(target)
    candidates = [
        root / "memory.jsonl",
        root / "learning" / "feedback.jsonl",
        root / "learning" / "patterns.jsonl",
        root / "learning" / "mistakes.jsonl",
        root / "learning" / "learnings.jsonl",
        root / "memory" / "memory.jsonl",
        root / "memory" / "feedback.jsonl",
    ]
    return [path for path in candidates if path.is_file()]


def selected_memory_root(target: Path, before: dict | None = None) -> Path:
    settings = before or load_install_state(target)
    raw = Path(str(settings.get("memory_path") or ".codex/anyone-can-code/memory/notes"))
    notes = raw if raw.is_absolute() else target / raw
    return notes.resolve().parent


def migrate_legacy_memory(target: Path, before: dict | None = None) -> dict:
    sources = legacy_memory_sources(target)
    if not sources:
        return {
            "status": "not found",
            "operation": "legacy-jsonl",
            "sources": [],
            "imported_count": 0,
            "skipped_count": 0,
        }
    old_root = os.environ.get("ACC_MCP_DATA_ROOT")
    os.environ["ACC_MCP_DATA_ROOT"] = str(selected_memory_root(target, before))
    try:
        return load_memory_server().migrate_legacy_jsonl(
            {
                "paths": [str(path) for path in sources],
                "scope": "project",
                "project_root": str(target),
            }
        )
    finally:
        if old_root is None:
            os.environ.pop("ACC_MCP_DATA_ROOT", None)
        else:
            os.environ["ACC_MCP_DATA_ROOT"] = old_root


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


def migrate(target: Path) -> None:
    before = load_install_state(target)
    before_version = before.get("plugin_version", "0.0.0")
    info = runtime_info.build_runtime_info(target, PLUGIN_ROOT)
    source_version = info.get("plugin_source_version") or plugin_version()
    runtime_version = info.get("installed_runtime_version")
    hook_mode = before.get("hook_mode", "bundled")

    print(f"Project: {before_version or 'unknown'}")
    print(f"Source: {source_version or 'missing'}")
    print(f"Runtime: {runtime_version or 'missing'}")
    print(f"Project root: {info['project_root']}")

    if info.get("marketplace_root"):
        print(f"Market: {info['marketplace_root']}")
    if info.get("marketplace_name"):
        configured = "yes" if info.get("managed_marketplace_configured") else "no"
        mode = info.get("marketplace_upgrade_mode", "none")
        print(f"Managed market: {configured} ({mode})")
    if info.get("plugin_source_root"):
        print(f"Source root: {info['plugin_source_root']}")
    if info.get("installed_plugin_root"):
        print(f"Runtime root: {info['installed_plugin_root']}")

    next_action = info.get("next_action", "unknown")
    if next_action == "same-everywhere":
        print("Need: nothing")
        print("Same everywhere.")
        return
    if next_action == "refresh-plugin-first":
        print("Need: refresh")
        print("Refresh plugin through Codex marketplace first.")
        if not info.get("managed_marketplace_configured") and info.get("marketplace_root"):
            print(f"Add market: codex plugin marketplace add \"{info['marketplace_root']}\"")
        print("Restart Codex. Open new thread.")
        return
    if next_action == "project-ahead-of-runtime":
        print("Need: stop")
        print("Project ahead of runtime.")
        print("Refresh runtime first.")
        return
    if next_action == "runtime-ahead-of-source":
        print("Need: stop")
        print("Runtime ahead of source.")
        print("Source tree stale.")
        return
    if next_action == "missing-runtime-and-source":
        print("Need: stop")
        print("Source and runtime missing.")
        if info.get("wrong_root_hint"):
            print(f"Maybe wrong root: {info['wrong_root_hint']}")
        return
    if next_action != "migrate-project":
        print("Need: stop")
        print("Update truth unclear.")
        return

    backup = backup_dir(target, before_version)
    backup_supported_data(target, backup)
    quarantined = quarantine_corrupt_files(target)
    memory_receipt = migrate_legacy_memory(target, before)
    if memory_receipt["status"] == "rolled_back":
        print("Need: stop")
        print("Memory migration rolled back.")
        print(f"Receipt: {memory_receipt['rollback_receipt_path']}")
        return
    run_setup(target, hook_mode, before)

    install_state = install_state_path(target)
    install_state.parent.mkdir(parents=True, exist_ok=True)
    install_state.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "plugin_version": runtime_version,
                "installed_via": "update.py",
                "hook_mode": hook_mode,
                "memory_mode": "portable-markdown",
                "memory_path": before.get("memory_path", ".codex/anyone-can-code/memory/notes"),
                "viewer_mode": before.get("viewer_mode", "none"),
                "mcp_server": "memory",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    journal = write_migration_journal(
        target,
        before_version,
        runtime_version,
        quarantined,
        memory_receipt,
    )
    doctor = run_doctor(target)
    print("Need: migrate")
    print(f"Update done: {before_version} -> {runtime_version}")
    print(f"Backup: {backup}")
    print(f"Journal: {journal}")
    if memory_receipt["status"] == "verified":
        print(
            f"Legacy memory: {memory_receipt['imported_count']} imported, "
            f"{memory_receipt['skipped_count']} duplicate skipped."
        )
        print(f"Memory receipt: {memory_receipt['receipt_path']}")
    else:
        print("Legacy memory: none found.")
    if quarantined:
        print("Bad files moved:")
        for item in quarantined:
            print(f"- {item}")
    if doctor and "summary" in doctor:
        summary = doctor["summary"]
        print(f"Doctor: {summary['pass']} PASS, {summary['warn']} WARN, {summary['fail']} FAIL")
    print("Memory: portable Markdown. Viewer: none.")
    print("Restart Codex. Open new thread.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate Anyone Can Code project state to the current plugin version")
    parser.add_argument("target", nargs="?", default=".", help="Project directory")
    parser.add_argument("--check", action="store_true", help="Show version drift only")
    parser.add_argument("--version", action="store_true", help="Print plugin version and exit")
    args = parser.parse_args()

    if args.version:
        print(plugin_version())
        return

    target = Path(args.target).resolve()
    if args.check:
        print(json.dumps(runtime_info.build_runtime_info(target, PLUGIN_ROOT), indent=2))
        return

    migrate(target)


if __name__ == "__main__":
    main()
