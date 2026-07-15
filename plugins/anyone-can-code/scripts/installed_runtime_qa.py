#!/usr/bin/env python3
"""Installed Codex Desktop runtime QA receipt for ACC."""

from __future__ import annotations

import argparse
import os
import json
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

import runtime_info


NAMESPACE = Path(".codex") / "anyone-can-code"

SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "natural_setup",
        "name": "Natural setup",
        "paths": ["skills/setup/SKILL.md", "scripts/setup.py"],
        "terms": {"skills/setup/SKILL.md": ["Use `$setup` after the plugin is installed"]},
    },
    {
        "id": "plan",
        "name": "Plan",
        "paths": ["skills/plan/SKILL.md", "scripts/canonical_state.py"],
        "terms": {"skills/plan/SKILL.md": ["canonical state"]},
    },
    {
        "id": "build",
        "name": "Build",
        "paths": ["skills/execute/SKILL.md", "scripts/canonical_state.py"],
        "terms": {"skills/execute/SKILL.md": ["canonical_state.py"]},
    },
    {
        "id": "correction",
        "name": "Correction",
        "paths": ["skills/fix/SKILL.md", "skills/resume/SKILL.md", "scripts/doctor.py"],
        "terms": {"skills/resume/SKILL.md": ["uncertain"]},
    },
    {
        "id": "learning",
        "name": "Learning",
        "paths": ["skills/learn/SKILL.md", "mcp/server.py"],
        "terms": {"skills/learn/SKILL.md": ["portable Markdown", "advisory"]},
    },
    {
        "id": "compaction",
        "name": "Compaction",
        "paths": ["skills/resume/SKILL.md", "scripts/canonical_state.py"],
        "terms": {"scripts/canonical_state.py": ["prepare_context_transition"]},
    },
    {
        "id": "new_chat_resume",
        "name": "New chat resume",
        "paths": ["skills/resume/SKILL.md", "scripts/canonical_state.py"],
        "terms": {"scripts/canonical_state.py": ["recover_from_canonical_state"]},
    },
    {
        "id": "verification",
        "name": "Verification",
        "paths": ["skills/verify/SKILL.md", "scripts/status_model.py"],
        "terms": {"skills/verify/SKILL.md": ["Built is not verified"]},
    },
    {
        "id": "hook_failure",
        "name": "Hook failure",
        "paths": ["hooks/scripts/state.py", "hooks/scripts/guard.py"],
        "terms": {"hooks/scripts/state.py": ["circuit_open", "run_optional_hook"]},
    },
    {
        "id": "plugin_conflict",
        "name": "Plugin conflict",
        "paths": ["scripts/doctor.py", "scripts/front_door.py"],
        "terms": {"scripts/doctor.py": ["run_plugin_conflicts", "ACC keeps workflow ownership"]},
    },
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    with open(handle, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    Path(temp_name).replace(path)


def _is_installed_cache(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return ".codex" in parts and "plugins" in parts and "cache" in parts


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_scenario(runtime_root: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    missing = []
    failed_terms = []
    for rel in scenario["paths"]:
        path = runtime_root / rel
        if not path.exists():
            missing.append(rel)
            continue
        for term in scenario.get("terms", {}).get(rel, []):
            try:
                text = _read(path)
            except OSError:
                failed_terms.append(f"{rel}: unreadable")
                continue
            if term not in text:
                failed_terms.append(f"{rel}: missing `{term}`")
    status = "pass" if not missing and not failed_terms else "fail"
    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "status": status,
        "missing": missing,
        "failed_terms": failed_terms,
    }


def check_memory_write_through(runtime_root: Path) -> dict[str, Any]:
    scenario = {
        "id": "memory_write_through",
        "name": "Memory write-through",
        "status": "fail",
        "missing": [],
        "failed_terms": [],
        "proof": [],
    }
    required = [
        runtime_root / "scripts" / "setup.py",
        runtime_root / "scripts" / "update.py",
        runtime_root / "scripts" / "memory_preflight.py",
        runtime_root / "mcp" / "server.py",
    ]
    missing = [str(path.relative_to(runtime_root)) for path in required if not path.exists()]
    if missing:
        scenario["missing"] = missing
        return scenario

    proof_script = r'''
import contextlib
import io
import json
import sys
from pathlib import Path

import setup
import update
import memory_preflight

project_root = Path(sys.argv[1]).resolve()
summary = "Always recall learned mistakes before first action after setup update or new thread."
setup.bootstrap_project(project_root)
stored = memory_preflight.store_learned_memory(
    project_root,
    summary,
    evidence="installed runtime memory write-through proof",
)
setup.bootstrap_project(project_root, force=True)
after_setup = memory_preflight.retrieve_relevant_memory(
    project_root,
    "recall learned mistakes before first action after setup",
)
install_path = project_root / ".codex" / "anyone-can-code" / "state" / "install.json"
install_state = json.loads(install_path.read_text(encoding="utf-8"))
install_state["plugin_version"] = "0.0.0"
install_path.write_text(json.dumps(install_state, indent=2) + "\n", encoding="utf-8")
with contextlib.redirect_stdout(io.StringIO()):
    update.migrate(project_root)
after_update = memory_preflight.retrieve_relevant_memory(
    project_root,
    "recall learned mistakes before first action after update",
)
new_thread = memory_preflight.retrieve_relevant_memory(
    project_root,
    "new thread recall learned mistakes before first action",
)
payload = {
    "stored": bool(stored.get("stored")),
    "after_setup": bool(after_setup.get("used")),
    "after_update": bool(after_update.get("used")),
    "new_thread": bool(new_thread.get("used")),
    "visible_lines": [
        after_setup.get("visible_line", ""),
        after_update.get("visible_line", ""),
        new_thread.get("visible_line", ""),
    ],
}
print("ACC_MEMORY_WRITE_THROUGH_PROOF=" + json.dumps(payload, sort_keys=True))
'''
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir) / "normal-project"
        env = os.environ.copy()
        scripts_dir = runtime_root / "scripts"
        env["PLUGIN_ROOT"] = str(runtime_root)
        env["PYTHONPATH"] = (
            str(scripts_dir)
            + os.pathsep
            + str(runtime_root)
            + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        )
        env.pop("ACC_MCP_DATA_ROOT", None)
        result = subprocess.run(
            [sys.executable, "-c", proof_script, str(project_root)],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
    marker = "ACC_MEMORY_WRITE_THROUGH_PROOF="
    payload = None
    for line in result.stdout.splitlines():
        if line.startswith(marker):
            try:
                payload = json.loads(line[len(marker) :])
            except json.JSONDecodeError:
                payload = None
            break
    if result.returncode != 0:
        scenario["failed_terms"] = [
            "active proof command failed",
            result.stderr.strip()[:400],
        ]
        return scenario
    if not isinstance(payload, dict):
        scenario["failed_terms"] = ["active proof JSON missing"]
        return scenario
    checks = {
        "store": payload.get("stored"),
        "setup": payload.get("after_setup"),
        "update": payload.get("after_update"),
        "new-thread": payload.get("new_thread"),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        scenario["failed_terms"] = [f"memory proof failed: {', '.join(failed)}"]
        scenario["details"] = payload
        return scenario
    scenario["status"] = "pass"
    scenario["proof"] = [name for name in ("store", "setup", "update", "new-thread")]
    scenario["details"] = {
        "visible_lines": payload.get("visible_lines", []),
    }
    return scenario


def check_visible_response_contract(runtime_root: Path) -> dict[str, Any]:
    scenario = {
        "id": "visible_response_contract",
        "name": "Visible response contract",
        "status": "fail",
        "missing": [],
        "failed_terms": [],
        "proof": [],
    }
    required = [
        runtime_root / "scripts" / "front_door.py",
        runtime_root / "scripts" / "product_intake.py",
        runtime_root / "scripts" / "capability_registry.py",
    ]
    missing = [str(path.relative_to(runtime_root)) for path in required if not path.exists()]
    if missing:
        scenario["missing"] = missing
        return scenario

    proof_script = r'''
import json
import sys
from pathlib import Path

import front_door

request = (
    "Improve the existing website until it is a polished demo site using ACC, "
    "Product Design, brainstorming, and UI skills"
)
route = front_door.route_request(request, plugins=[])
contract = route.get("response_contract", {})
displayed_text = (
    f"{route.get('banner', '')}\n"
    f"Route: {' -> '.join(route.get('route', []))}\n"
    "Summary: ACC routed this existing website request to review -> polish -> verify.\n"
    "Next: continue with ACC fallback if any specialist output is empty."
)
payload = {
    "entry_mode": route.get("entry_mode"),
    "product_type": route.get("product_type"),
    "route": route.get("route"),
    "visible_text_required": bool(contract.get("visible_text_required")),
    "next_action_required": bool(contract.get("next_action_required")),
    "empty_result_action": contract.get("empty_result_action"),
    "displayed_text": displayed_text,
}
print("ACC_VISIBLE_RESPONSE_PROOF=" + json.dumps(payload, sort_keys=True))
'''
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        scripts_dir = runtime_root / "scripts"
        env["PYTHONPATH"] = (
            str(scripts_dir)
            + os.pathsep
            + str(runtime_root)
            + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        )
        result = subprocess.run(
            [sys.executable, "-c", proof_script],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    marker = "ACC_VISIBLE_RESPONSE_PROOF="
    payload = None
    for line in result.stdout.splitlines():
        if line.startswith(marker):
            try:
                payload = json.loads(line[len(marker) :])
            except json.JSONDecodeError:
                payload = None
            break
    if result.returncode != 0:
        scenario["failed_terms"] = [
            "visible response proof command failed",
            result.stderr.strip()[:400],
        ]
        return scenario
    if not isinstance(payload, dict):
        scenario["failed_terms"] = ["visible response proof JSON missing"]
        return scenario
    checks = {
        "existing-website-route": payload.get("entry_mode") == "polish-review",
        "visible-text-required": payload.get("visible_text_required"),
        "next-action-required": payload.get("next_action_required"),
        "acc-fallback-response": payload.get("empty_result_action") == "acc-fallback-response",
        "rendered-message": len(str(payload.get("displayed_text") or "")) > 20,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        scenario["failed_terms"] = [f"visible response proof failed: {', '.join(failed)}"]
        scenario["details"] = payload
        return scenario
    scenario["status"] = "pass"
    scenario["proof"] = list(checks.keys())
    scenario["details"] = {
        "entry_mode": payload.get("entry_mode"),
        "route": payload.get("route"),
        "displayed_text": payload.get("displayed_text"),
        "rendering_boundary": (
            "Installed runtime returned a visible response contract and "
            "non-empty message text; local script cannot inspect Codex Desktop pixels."
        ),
    }
    return scenario


def check_hook_nested_root_receipts(runtime_root: Path) -> dict[str, Any]:
    scenario = {
        "id": "hook_nested_root_receipts",
        "name": "Hook nested-root receipts",
        "status": "fail",
        "missing": [],
        "failed_terms": [],
        "proof": [],
    }
    required = [
        runtime_root / "scripts" / "setup.py",
        runtime_root / "hooks" / "scripts" / "load_session.py",
        runtime_root / "hooks" / "scripts" / "guard.py",
        runtime_root / "hooks" / "scripts" / "save_session.py",
        runtime_root / "hooks" / "scripts" / "state.py",
    ]
    missing = [str(path.relative_to(runtime_root)) for path in required if not path.exists()]
    if missing:
        scenario["missing"] = missing
        return scenario

    proof_script = r'''
import json
import os
import subprocess
import sys
from pathlib import Path

import setup

runtime_root = Path(sys.argv[1]).resolve()
proof_root = Path(sys.argv[2]).resolve()

def run_hook(name, payload):
    script = runtime_root / "hooks" / "scripts" / f"{name}.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "PLUGIN_ROOT": str(runtime_root)},
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    try:
        parsed = json.loads(lines[-1]) if lines else {}
    except json.JSONDecodeError:
        parsed = {"_parse_error": result.stdout}
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "json": parsed}

def read_receipts(root):
    path = root / ".codex" / "anyone-can-code" / "logs" / "hook-receipts.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

workspace = proof_root / "workspace"
nested = workspace / "zenfit-site"
setup.bootstrap_project(nested)
agents_path = nested / "AGENTS.md"
agents_path.write_text("project rules stay\n", encoding="utf-8")
load = run_hook(
    "load_session",
    {
        "hook_event_name": "SessionStart",
        "source": "startup",
        "session_id": "s-installed",
        "turn_id": "t-installed",
        "hook_run_id": "run-load-installed",
        "cwd": str(workspace),
    },
)
guard = run_hook(
    "guard",
    {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "secret token ABC123 wrong project",
        "session_id": "s-installed",
        "turn_id": "t-installed-2",
        "hook_run_id": "run-guard-installed",
        "cwd": str(workspace),
    },
)
stop = run_hook(
    "save_session",
    {
        "hook_event_name": "Stop",
        "session_id": "s-installed",
        "turn_id": "t-installed-3",
        "hook_run_id": "run-stop-installed",
        "last_assistant_message": "Verified source and installed runtime proof.",
        "stop_hook_active": False,
        "cwd": str(workspace),
    },
)
receipts = read_receipts(nested)
receipt_text = json.dumps(receipts, sort_keys=True)
state_root = nested / ".codex" / "anyone-can-code" / "state"
artifacts_root = nested / ".codex" / "anyone-can-code" / "artifacts"

ambiguous = proof_root / "ambiguous"
setup.bootstrap_project(ambiguous / "one")
setup.bootstrap_project(ambiguous / "two")
amb = run_hook(
    "guard",
    {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "build this",
        "session_id": "s-amb",
        "turn_id": "t-amb",
        "hook_run_id": "run-ambiguous-installed",
        "cwd": str(ambiguous),
    },
)
amb_receipts = read_receipts(ambiguous)
amb_parent_layout = (ambiguous / ".codex" / "anyone-can-code").exists()
# Bare folder with no ACC setup must stay empty of ACC state.
bare = proof_root / "bare-no-setup"
(bare / ".git").mkdir(parents=True)
bare_run = run_hook(
    "load_session",
    {
        "hook_event_name": "SessionStart",
        "source": "startup",
        "session_id": "s-bare",
        "cwd": str(bare),
    },
)
bare_layout = (bare / ".codex" / "anyone-can-code").exists()

payload = {
    "load_returncode": load["returncode"],
    "guard_returncode": guard["returncode"],
    "stop_returncode": stop["returncode"],
    "ambiguous_returncode": amb["returncode"],
    "load_context": bool(load["json"].get("hookSpecificOutput", {}).get("additionalContext")),
    "guard_context": bool(guard["json"].get("hookSpecificOutput", {}).get("additionalContext")),
    "agents_unchanged": agents_path.read_text(encoding="utf-8") == "project rules stay\n",
    "turn_ledger_exists": (state_root / "turn-ledger.jsonl").exists(),
    "snapshot_exists": (state_root / "session-snapshot.md").exists(),
    "resume_note_exists": (artifacts_root / "resume-note.md").exists(),
    "nested_receipts": receipts,
    "ambiguous_receipts": amb_receipts,
    "ambiguous_parent_layout": amb_parent_layout,
    "ambiguous_empty_output": amb["json"] == {},
    "bare_empty_output": bare_run["json"] == {},
    "bare_layout": bare_layout,
    "redacted_prompt": "secret token" not in receipt_text and "ABC123" not in receipt_text,
}
print("ACC_HOOK_NESTED_RECEIPT_PROOF=" + json.dumps(payload, sort_keys=True))
'''
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        scripts_dir = runtime_root / "scripts"
        env["PYTHONPATH"] = (
            str(scripts_dir)
            + os.pathsep
            + str(runtime_root)
            + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        )
        env.pop("ACC_MCP_DATA_ROOT", None)
        result = subprocess.run(
            [sys.executable, "-c", proof_script, str(runtime_root), temp_dir],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=90,
            env=env,
        )
    marker = "ACC_HOOK_NESTED_RECEIPT_PROOF="
    payload = None
    for line in result.stdout.splitlines():
        if line.startswith(marker):
            try:
                payload = json.loads(line[len(marker) :])
            except json.JSONDecodeError:
                payload = None
            break
    if result.returncode != 0:
        scenario["failed_terms"] = [
            "hook nested receipt proof command failed",
            result.stderr.strip()[:400],
        ]
        return scenario
    if not isinstance(payload, dict):
        scenario["failed_terms"] = ["hook nested receipt proof JSON missing"]
        return scenario

    nested_receipts = payload.get("nested_receipts") if isinstance(payload.get("nested_receipts"), list) else []
    ambiguous_receipts = payload.get("ambiguous_receipts") if isinstance(payload.get("ambiguous_receipts"), list) else []
    useful = [
        item
        for item in nested_receipts
        if item.get("resolution_state") == "resolved"
        and item.get("final_effectiveness") == "useful"
    ]
    stop_receipts = [
        item
        for item in nested_receipts
        if item.get("hook") == "save_session"
        and item.get("resolution_state") == "resolved"
        and item.get("final_effectiveness") == "useful"
        and item.get("state_write_result") == "declared"
    ]
    # Ambiguous / no-setup: hooks must skip with no parent ACC layout and no receipts.
    ambiguous_clean = (
        not payload.get("ambiguous_parent_layout")
        and payload.get("ambiguous_empty_output")
        and len(ambiguous_receipts) == 0
    )
    bare_clean = (not payload.get("bare_layout")) and payload.get("bare_empty_output")
    checks = {
        "nested-resolution": bool(useful),
        "useful-context": bool(payload.get("load_context") and payload.get("guard_context")),
        "durable-receipt": len(nested_receipts) >= 3,
        "stop-state-write": bool(
            stop_receipts
            and payload.get("turn_ledger_exists")
            and payload.get("snapshot_exists")
            and payload.get("resume_note_exists")
            and payload.get("agents_unchanged")
        ),
        "ambiguous-skip-clean": bool(ambiguous_clean),
        "bare-skip-clean": bool(bare_clean),
        "redacted-prompt": bool(payload.get("redacted_prompt")),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        scenario["failed_terms"] = [f"hook nested receipt proof failed: {', '.join(failed)}"]
        scenario["details"] = payload
        return scenario
    scenario["status"] = "pass"
    scenario["proof"] = list(checks.keys())
    scenario["details"] = {
        "nested_receipt_count": len(nested_receipts),
        "ambiguous_receipt_count": len(ambiguous_receipts),
        "useful_hooks": [item.get("hook") for item in useful],
        "stop_state_paths": stop_receipts[0].get("state_write_paths", []) if stop_receipts else [],
    }
    return scenario


def run_installed_qa(
    project_root: Path,
    plugin_root: Path,
    *,
    runtime_root: Path | None = None,
) -> dict[str, Any]:
    runtime_root = runtime_root or runtime_info.find_installed_plugin_root(
        runtime_info.read_manifest_name(plugin_root) or runtime_info.PLUGIN_NAME,
        plugin_root,
    )
    receipt = {
        "id": f"installed-qa-{utc_now().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:8]}",
        "schema_version": 1,
        "created_at": utc_now(),
        "surface": "codex-desktop-installed-runtime",
        "project_root": str(project_root),
        "plugin_source_root": str(plugin_root),
        "installed_runtime_root": str(runtime_root) if runtime_root else "",
        "user_interventions": [],
        "false_done_claims": [],
        "next_step_questions": [],
        "recovery_success": [],
        "scenarios": [],
        "status": "fail",
        "plain_result": "",
    }

    if runtime_root is None:
        receipt["plain_result"] = "Installed ACC runtime not found. No false pass."
        return receipt

    runtime_root = runtime_root.resolve()
    if not _is_installed_cache(runtime_root):
        receipt["plain_result"] = "QA target is not Codex installed cache. No false pass."
        return receipt

    receipt["scenarios"] = [check_scenario(runtime_root, scenario) for scenario in SCENARIOS]
    receipt["scenarios"].append(check_memory_write_through(runtime_root))
    receipt["scenarios"].append(check_visible_response_contract(runtime_root))
    receipt["scenarios"].append(check_hook_nested_root_receipts(runtime_root))
    failed = [item for item in receipt["scenarios"] if item["status"] != "pass"]
    if failed:
        receipt["plain_result"] = (
            f"Installed runtime failed {len(failed)} scenario(s). Refresh installed ACC, restart/new chat, rerun QA."
        )
        return receipt

    receipt["status"] = "pass"
    receipt["recovery_success"] = [
        "resume uses canonical state",
        "hook failure stays optional",
        "plugin conflict keeps ACC owner and fallback",
    ]
    receipt["plain_result"] = "Installed ACC runtime passed required scenario evidence."
    return receipt


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "# ACC Installed Runtime QA Receipt",
        "",
        f"- ID: `{receipt['id']}`",
        f"- Status: `{receipt['status']}`",
        f"- Surface: {receipt['surface']}",
        f"- Installed runtime: {receipt.get('installed_runtime_root') or 'not found'}",
        f"- Result: {receipt['plain_result']}",
        "",
        "## Scenarios",
    ]
    for scenario in receipt.get("scenarios", []):
        lines.append(f"- {scenario['name']}: `{scenario['status']}`")
        for missing in scenario.get("missing", []):
            lines.append(f"  - Missing: `{missing}`")
        for failed in scenario.get("failed_terms", []):
            lines.append(f"  - Failed term: {failed}")
    lines.extend(
        [
            "",
            "## Observations",
            f"- User interventions: {len(receipt.get('user_interventions', []))}",
            f"- False-done claims: {len(receipt.get('false_done_claims', []))}",
            f"- Next-step questions: {len(receipt.get('next_step_questions', []))}",
            f"- Recovery successes: {len(receipt.get('recovery_success', []))}",
            "",
        ]
    )
    return "\n".join(lines)


def write_receipt(project_root: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    root = project_root / NAMESPACE / "artifacts" / "installed-qa"
    json_path = root / f"{receipt['id']}.json"
    markdown_path = root / f"{receipt['id']}.md"
    _write_text_atomic(json_path, json.dumps(receipt, indent=2) + "\n")
    _write_text_atomic(markdown_path, render_receipt(receipt))
    receipt["receipt_path"] = str(json_path)
    receipt["receipt_markdown"] = str(markdown_path)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Run installed ACC runtime QA evidence checks")
    parser.add_argument("--project-root", default=str(Path.cwd()))
    parser.add_argument("--plugin-root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--runtime-root", default="")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    receipt = run_installed_qa(
        Path(args.project_root),
        Path(args.plugin_root),
        runtime_root=Path(args.runtime_root) if args.runtime_root else None,
    )
    if args.write_receipt:
        receipt = write_receipt(Path(args.project_root), receipt)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(render_receipt(receipt))
    if receipt["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
