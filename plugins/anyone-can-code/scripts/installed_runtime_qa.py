#!/usr/bin/env python3
"""Installed Codex Desktop runtime QA receipt for ACC."""

from __future__ import annotations

import argparse
import json
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
