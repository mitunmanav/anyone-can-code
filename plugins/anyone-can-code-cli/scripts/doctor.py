#!/usr/bin/env python3
"""
Small doctor for Anyone Can Code.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import canonical_state
import front_door
import memory_preflight
import product_intake
import runtime_info
import status_model
import work_visibility


def plugin_root() -> Path:
    root = os.environ.get("PLUGIN_ROOT")
    if root:
        return Path(root)
    return Path(__file__).resolve().parent.parent


PLUGIN_ROOT = plugin_root()

SKILL_BUDGET_CHARS = 4000


def run_skill_budget(skills_root: Path | None = None) -> list[dict]:
    """Check every SKILL.md against the caveman token budget."""
    root = skills_root or (PLUGIN_ROOT / "skills")
    results: list[dict] = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        try:
            size = len(skill_md.read_text(encoding="utf-8"))
        except OSError:
            continue
        status = "FAIL" if size > SKILL_BUDGET_CHARS else "PASS"
        results.append({"status": status, "detail": f"{skill_md.parent.name}: {size} chars"})
    return results
PROJECT_ROOT = Path(os.environ.get("ACC_PROJECT_ROOT", Path.cwd()))
PROJECT_NAMESPACE = "anyone-can-code"
ALLOWED_PERSONA_MODES = {"builder", "developer", "mixed"}
ALLOWED_REPO_MODES = {"new", "existing", "production", "unknown"}
ACC_HOOK_DISABLE_MARKER = Path(".codex") / "anyone-can-code-hooks.disabled"
HOOK_HEALTH_FILE = Path(".codex") / PROJECT_NAMESPACE / "logs" / "hook-health.json"
HOOK_RECEIPTS_FILE = Path(".codex") / PROJECT_NAMESPACE / "logs" / "hook-receipts.jsonl"
STATE_AGREEMENT_FIELDS = (
    "persona_mode",
    "repo_mode",
    "communication_mode",
    "memory_mode",
    "viewer_mode",
)
WORKFLOW_CONTROL_WORDS = {
    "acc",
    "anyone",
    "workflow",
    "orchestrator",
    "project state",
    "canonical state",
}


def acc_hook_disable_marker(project_root: Path) -> Path | None:
    current = project_root.resolve()
    for candidate in (current, *current.parents):
        marker = candidate / ACC_HOOK_DISABLE_MARKER
        try:
            if marker.is_file():
                return marker
        except OSError:
            continue
    return None


class Doctor:
    def __init__(self, json_mode: bool = False) -> None:
        self.json_mode = json_mode
        self.results: list[dict] = []

    def check(self, category: str, name: str, status: str, severity: str, evidence: str) -> None:
        entry = {
            "category": category,
            "check": name,
            "status": status,
            "severity": severity,
            "evidence": evidence,
        }
        self.results.append(entry)
        if not self.json_mode:
            print(f"[{status}] {category}/{name}")
            if evidence:
                print(f"  {evidence}")

    def syntax_ok(self, path: Path) -> tuple[bool, str]:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            return True, ""
        except SyntaxError as exc:
            line = exc.lineno or "?"
            return False, f"{path.name}:{line}: {exc.msg}"
        except OSError as exc:
            return False, str(exc)

    def run_python(self) -> None:
        if sys.version_info >= (3, 8):
            self.check("capability", "python_version", "PASS", "info", sys.version.split()[0])
        else:
            self.check("capability", "python_version", "FAIL", "blocking", f"Python 3.8+ required, found {sys.version}")

    def run_manifest(self) -> None:
        path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        if not path.exists():
            self.check("config", "manifest_present", "FAIL", "blocking", "plugin.json not found")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.check("config", "manifest_present", "FAIL", "blocking", f"Invalid JSON: {exc}")
            return
        for key in ["name", "version", "description", "skills", "hooks", "mcpServers"]:
            if key not in data:
                self.check("config", f"manifest_{key}", "FAIL", "blocking", f"Missing '{key}'")
                return
        self.check("config", "manifest_present", "PASS", "info", f"{data['name']} v{data['version']}")

    def run_hooks_bundle(self) -> None:
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        if not hooks_json.exists():
            self.check("capability", "bundled_hooks", "FAIL", "blocking", "hooks/hooks.json missing")
            return
        self.check("capability", "bundled_hooks", "PASS", "info", "hooks/hooks.json present (CLI package)")
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.check("capability", "hooks_cli_port", "FAIL", "blocking", f"hooks.json invalid: {exc}")
            return
        missing_timeout = 0
        powershell_only = 0
        total = 0
        for groups in (data.get("hooks") or {}).values():
            for group in groups or []:
                for hook in group.get("hooks") or []:
                    if hook.get("type", "command") != "command":
                        continue
                    total += 1
                    cmd = str(hook.get("command") or "")
                    if not isinstance(hook.get("timeout"), int) or hook["timeout"] <= 0:
                        missing_timeout += 1
                    if "powershell" in cmd.lower() or "encodedcommand" in cmd.lower():
                        powershell_only += 1
                    if "PLUGIN_ROOT" not in cmd:
                        powershell_only += 1
        if total == 0:
            self.check("capability", "hooks_cli_port", "FAIL", "blocking", "no command hooks found")
        elif missing_timeout or powershell_only:
            self.check(
                "capability",
                "hooks_cli_port",
                "FAIL",
                "blocking",
                f"CLI port gaps: missing_timeout={missing_timeout} non_portable_command={powershell_only}",
            )
        else:
            self.check(
                "capability",
                "hooks_cli_port",
                "PASS",
                "info",
                f"{total} hooks portable command + timeout (CLI package)",
            )

    def run_hook_scripts(self) -> None:
        scripts_dir = PLUGIN_ROOT / "hooks" / "scripts"
        expected = ["state.py", "guard.py", "audit.py", "load_session.py", "save_session.py"]
        missing = [name for name in expected if not (scripts_dir / name).exists()]
        if missing:
            self.check("capability", "hook_scripts", "FAIL", "blocking", f"Missing hook scripts: {missing}")
            return
        failures = []
        for name in expected:
            ok, evidence = self.syntax_ok(scripts_dir / name)
            if not ok:
                failures.append(evidence or name)
        if failures:
            self.check("capability", "hook_scripts", "FAIL", "blocking", f"Syntax failures: {failures}")
        else:
            self.check("capability", "hook_scripts", "PASS", "info", f"{len(expected)} hook scripts parse")

    def run_skills(self) -> None:
        skills_dir = PLUGIN_ROOT / "skills"
        if not skills_dir.exists():
            self.check("config", "skills_dir", "FAIL", "blocking", "skills directory missing")
            return
        skill_dirs = [item for item in skills_dir.iterdir() if item.is_dir()]
        total_desc_chars = 0
        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                self.check("config", f"skill_{skill_dir.name}", "WARN", "warning", "Missing SKILL.md")
                continue
            for line in skill_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("description:"):
                    total_desc_chars += len(line)
                    break
        self.check("capability", "skills_count", "PASS", "info", f"{len(skill_dirs)} skill folders")
        status = "WARN" if total_desc_chars > 7000 else "PASS"
        severity = "warning" if total_desc_chars > 7000 else "info"
        self.check("config", "skills_description_budget", status, severity, f"Approx {total_desc_chars} description chars")

    def run_mcp(self) -> None:
        path = PLUGIN_ROOT / ".mcp.json"
        if not path.exists():
            self.check("config", "mcp_config", "WARN", "warning", "No .mcp.json present")
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.check("config", "mcp_config", "FAIL", "blocking", f"Invalid .mcp.json: {exc}")
            return
        if "mcp_servers" in payload:
            self.check("config", "mcp_schema", "FAIL", "blocking", "Use camelCase 'mcpServers', not legacy 'mcp_servers'")
            return
        servers = payload.get("mcpServers", {})
        if not servers:
            self.check("config", "mcp_config", "FAIL", "blocking", "No bundled MCP server declared")
            return
        scripts = []
        for server_name, server in servers.items():
            command = str(server.get("command", "")).strip()
            args = server.get("args", []) or []
            if not command:
                self.check("config", f"mcp_{server_name}", "FAIL", "blocking", "MCP command missing")
                return
            if command.lower() == "python" and args:
                script_rel = str(args[0])
                script_path = (PLUGIN_ROOT / script_rel).resolve()
                scripts.append(script_path)
                if not script_path.exists():
                    self.check("config", f"mcp_{server_name}", "FAIL", "blocking", f"Missing MCP script: {script_rel}")
                    return
                ok, evidence = self.syntax_ok(script_path)
                if not ok:
                    self.check("config", f"mcp_{server_name}", "FAIL", "blocking", f"MCP script syntax failed: {evidence or script_rel}")
                    return
        self.check("capability", "mcp_config", "PASS", "info", f"{len(servers)} bundled MCP server(s) ready")

    def run_project_layout(self) -> None:
        namespace_root = PROJECT_ROOT / ".codex" / PROJECT_NAMESPACE
        if namespace_root.exists():
            self.check("recovery", "project_layout", "PASS", "info", str(namespace_root))
        else:
            self.check("recovery", "project_layout", "WARN", "warning", "Project bootstrap has not created .codex/anyone-can-code yet")

    def run_project_selection(self, selection: dict) -> None:
        if selection["status"] == "ambiguous":
            self.check(
                "recovery",
                "project_selection",
                "FAIL",
                "blocking",
                "Multiple ACC projects found. Choose one: "
                + ", ".join(selection["candidates"]),
            )
            return
        selected = str(selection["project_root"])
        requested = str(selection["requested_root"])
        if selected != requested:
            self.check(
                "recovery",
                "project_selection",
                "WARN",
                "warning",
                f"Selected nested ACC project: {selected}",
            )
            return
        self.check(
            "recovery",
            "project_selection",
            "PASS",
            "info",
            f"Using requested project root: {selected}",
        )

    def read_project_json(self, path: Path) -> tuple[dict | None, str]:
        try:
            return json.loads(path.read_text(encoding="utf-8")), ""
        except FileNotFoundError:
            return None, f"Missing {path}"
        except json.JSONDecodeError as exc:
            return None, f"Invalid JSON: {exc}"
        except OSError as exc:
            return None, str(exc)

    def plain_next(self, message: str, action: str) -> str:
        return f"{message} Next: {action}"

    def run_project_state(self) -> None:
        namespace_root = PROJECT_ROOT / ".codex" / PROJECT_NAMESPACE
        preferences_path = namespace_root / "settings" / "preferences.json"
        workflow_path = namespace_root / "state" / "workflow.json"

        preferences, pref_error = self.read_project_json(preferences_path)
        workflow, workflow_error = self.read_project_json(workflow_path)

        if preferences is None:
            self.check("recovery", "persona_settings", "WARN", "warning", pref_error)
        else:
            persona_mode = preferences.get("persona_mode")
            allowed_modes = preferences.get("persona_allowed_modes")
            communication_mode = preferences.get("communication_mode")
            if (
                persona_mode in ALLOWED_PERSONA_MODES
                and allowed_modes == ["builder", "developer", "mixed"]
                and communication_mode == "caveman-strict"
            ):
                self.check("recovery", "persona_settings", "PASS", "info", f"{persona_mode}, {communication_mode}")
            else:
                self.check("recovery", "persona_settings", "WARN", "warning", "Persona defaults missing or invalid")

        if workflow is None:
            self.check("recovery", "workflow_state", "WARN", "warning", workflow_error)
            self.check("recovery", "workflow_observability", "WARN", "warning", workflow_error)
            self.check("recovery", "legacy_state_fields", "WARN", "warning", workflow_error)
        else:
            setup_state = workflow.get("setup_state")
            workflow_persona = workflow.get("persona_mode")
            if setup_state == "ready" and workflow_persona in ALLOWED_PERSONA_MODES:
                self.check("recovery", "workflow_state", "PASS", "info", f"{setup_state}, {workflow_persona}")
            else:
                self.check("recovery", "workflow_state", "WARN", "warning", "Workflow setup state missing or invalid")
            verification = workflow.get("verification")
            if (
                isinstance(verification, dict)
                and str(verification.get("level") or "").strip()
                and isinstance(verification.get("evidence"), list)
                and isinstance(verification.get("stale"), bool)
                and workflow.get("transaction_id")
                and workflow.get("workflow_owner") == "acc"
            ):
                self.check(
                    "recovery",
                    "workflow_observability",
                    "PASS",
                    "info",
                    f"Canonical verification: {verification['level']}",
                )
            else:
                self.check(
                    "recovery",
                    "workflow_observability",
                    "WARN",
                    "warning",
                    "Canonical verification shape missing or invalid",
                )
            legacy_fields = canonical_state.legacy_truth_fields(workflow)
            if legacy_fields:
                self.check(
                    "recovery",
                    "legacy_state_fields",
                    "WARN",
                    "warning",
                    self.plain_next(
                        f"Legacy workflow truth fields remain: {', '.join(legacy_fields)}.",
                        "run setup or update to rewrite canonical state.",
                    ),
                )
            else:
                self.check(
                    "recovery",
                    "legacy_state_fields",
                    "PASS",
                    "info",
                    "No legacy workflow truth fields.",
                )

        if isinstance(preferences, dict) and isinstance(workflow, dict):
            mismatches = [
                field
                for field in STATE_AGREEMENT_FIELDS
                if preferences.get(field) != workflow.get(field)
            ]
            if mismatches:
                self.check(
                    "recovery",
                    "state_agreement",
                    "WARN",
                    "warning",
                    self.plain_next(
                        f"Settings and workflow disagree: {', '.join(mismatches)}.",
                        "run setup or update before continuing recovery.",
                    ),
                )
            else:
                self.check(
                    "recovery",
                    "state_agreement",
                    "PASS",
                    "info",
                    "Settings and workflow agree.",
                )
        else:
            self.check(
                "recovery",
                "state_agreement",
                "WARN",
                "warning",
                self.plain_next(
                    "Cannot compare settings and workflow.",
                    "run setup or update before continuing recovery.",
                ),
            )

        repo_mode = None
        if isinstance(preferences, dict):
            repo_mode = preferences.get("repo_mode")
        if repo_mode is None and isinstance(workflow, dict):
            repo_mode = workflow.get("repo_mode")
        if repo_mode in ALLOWED_REPO_MODES:
            self.check("recovery", "repo_mode", "PASS", "info", repo_mode)
        else:
            self.check("recovery", "repo_mode", "WARN", "warning", "Repo mode missing or invalid")

        memory_mode = preferences.get("memory_mode") if isinstance(preferences, dict) else None
        memory_path_value = preferences.get("memory_path") if isinstance(preferences, dict) else None
        if memory_path_value:
            memory_path = Path(str(memory_path_value))
            if not memory_path.is_absolute():
                memory_path = PROJECT_ROOT / memory_path
        else:
            memory_path = namespace_root / "memory" / "notes"
        if memory_mode == "portable-markdown" and memory_path.exists():
            self.check("memory", "memory_storage", "PASS", "info", f"portable Markdown: {memory_path}")
        else:
            self.check("memory", "memory_storage", "WARN", "warning", f"Markdown storage missing or unconfigured: {memory_path}")

        viewer_mode = preferences.get("viewer_mode", "none") if isinstance(preferences, dict) else "none"
        if viewer_mode == "none":
            self.check("memory", "memory_viewer", "PASS", "info", "Optional viewer not selected")
        elif viewer_mode == "obsidian":
            detected = shutil.which("obsidian") or shutil.which("Obsidian.exe")
            status = "PASS" if detected else "WARN"
            severity = "info" if detected else "warning"
            evidence = detected or "Obsidian selected but not detected; Markdown storage still works"
            self.check("memory", "memory_viewer", status, severity, evidence)
        else:
            self.check("memory", "memory_viewer", "WARN", "warning", f"Unsupported viewer mode: {viewer_mode}")

    def run_hook_health(self) -> None:
        health_path = PROJECT_ROOT / HOOK_HEALTH_FILE
        receipt_summary = self.latest_hook_receipt_summary()
        health, error = self.read_project_json(health_path)
        if health is None:
            if receipt_summary:
                self.check(
                    "recovery",
                    "hook_health",
                    "PASS",
                    "info",
                    self.plain_next(
                        f"No hook health file yet; {receipt_summary}.",
                        "keep receipts separate from Codex UI or telemetry claims.",
                    ),
                )
                return
            self.check(
                "recovery",
                "hook_health",
                "PASS",
                "info",
                self.plain_next(
                    "No hook health file yet; hooks are optional and core ACC still works.",
                    "enable hooks only if measured helper signals are wanted.",
                ),
            )
            return

        hooks = health.get("hooks")
        if not isinstance(hooks, dict):
            self.check(
                "recovery",
                "hook_health",
                "WARN",
                "warning",
                self.plain_next(
                    f"Hook health is unreadable: {error or 'hooks map missing'}.",
                    "delete the bad health file and let hooks recreate it.",
                ),
            )
            return

        broken = [
            name
            for name, entry in hooks.items()
            if isinstance(entry, dict)
            and (entry.get("status") == "fail" or entry.get("circuit_open"))
        ]
        if broken:
            self.check(
                "recovery",
                "hook_health",
                "WARN",
                "warning",
                self.plain_next(
                    f"Hook helper problem: {', '.join(sorted(broken))}.",
                    "continue from canonical state; repair hooks after restart or new-thread proof.",
                ),
            )
        else:
            self.check(
                "recovery",
                "hook_health",
                "PASS",
                "info",
                " ".join(
                    part
                    for part in [
                        f"{len(hooks)} hook helper record(s) healthy or skipped.",
                        receipt_summary,
                    ]
                    if part
                ),
            )

    def latest_hook_receipt_summary(self) -> str:
        path = PROJECT_ROOT / HOOK_RECEIPTS_FILE
        if not path.exists():
            return ""
        try:
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except OSError:
            return "latest receipts unreadable"
        rows = []
        for line in lines[-5:]:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                rows.append(value)
        if not rows:
            return "latest receipts unreadable"
        latest = rows[-1]
        states = sorted({str(row.get("final_effectiveness") or "unknown") for row in rows})
        latest_label = "/".join(
            part
            for part in [
                str(latest.get("hook") or "hook"),
                str(latest.get("hook_event") or "event"),
                str(latest.get("resolution_state") or "resolution"),
                str(latest.get("final_effectiveness") or "effectiveness"),
            ]
            if part
        )
        return f"latest receipts: {len(rows)} sampled; states {', '.join(states)}; latest {latest_label}"

    def run_project_config(self) -> None:
        config_path = PROJECT_ROOT / ".codex" / "config.toml"
        marker = acc_hook_disable_marker(PROJECT_ROOT)
        if marker is not None:
            self.check(
                "config",
                "project_hooks_mode",
                "PASS",
                "info",
                f"ACC-only marker active; other hooks stay enabled: {marker}",
            )
            return
        if not config_path.exists():
            self.check("config", "project_config", "WARN", "warning", "No project .codex/config.toml found")
            return
        text = config_path.read_text(encoding="utf-8")
        hook_off = "plugin_hooks = false" in text or "hooks = false" in text
        if hook_off:
            self.check("config", "project_hooks_mode", "PASS", "info", "Project config can keep hooks quiet here")
        else:
            self.check("config", "project_hooks_mode", "WARN", "warning", "Project config does not disable hooks here")
        # Item 13: native memories should stay off
        try:
            scripts = PLUGIN_ROOT / "scripts"
            if str(scripts) not in sys.path:
                sys.path.insert(0, str(scripts))
            from native_memory_policy import check_memories_off
            mem = check_memories_off(config_path)
            if mem["ok"]:
                self.check("config", "native_memories_off", "PASS", "info", mem["detail"])
            else:
                self.check(
                    "config",
                    "native_memories_off",
                    "WARN",
                    "warning",
                    f"Native Codex memories not off ({mem['detail']}). ACC uses two-drawer memory instead.",
                )
        except Exception:
            self.check("config", "native_memories_off", "WARN", "warning", "Could not check native memories flag")

    def run_default_prompts(self) -> None:
        path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.check("config", "default_prompt_limit", "WARN", "warning", "Could not validate default prompts")
            return
        prompts = payload.get("interface", {}).get("defaultPrompt", [])
        if len(prompts) > 3:
            self.check("config", "default_prompt_limit", "FAIL", "blocking", f"{len(prompts)} prompts found")
            return
        too_long = [prompt for prompt in prompts if len(prompt) > 128]
        if too_long:
            self.check("config", "default_prompt_limit", "FAIL", "blocking", "At least one default prompt exceeds 128 chars")
        else:
            self.check("config", "default_prompt_limit", "PASS", "info", f"{len(prompts)} prompts within docs limits")

    def run_usage_script(self) -> None:
        script_path = PLUGIN_ROOT / "scripts" / "codeburn.py"
        if not script_path.exists():
            self.check("verification", "usage_script", "WARN", "warning", "codeburn.py not found")
            return
        ok, evidence = self.syntax_ok(script_path)
        if ok:
            self.check("verification", "usage_script", "PASS", "info", "codeburn.py parses")
        else:
            self.check("verification", "usage_script", "FAIL", "blocking", evidence[:240])

    def run_work_visibility(self) -> None:
        script_path = PLUGIN_ROOT / "scripts" / "work_visibility.py"
        if not script_path.exists():
            self.check("verification", "work_visibility", "FAIL", "blocking", "work_visibility.py not found")
            return
        ok, evidence = self.syntax_ok(script_path)
        if not ok:
            self.check("verification", "work_visibility", "FAIL", "blocking", evidence[:240])
            return
        ok, evidence = work_visibility.smoke_check(PROJECT_ROOT)
        if ok:
            self.check("verification", "work_visibility", "PASS", "info", evidence)
        else:
            self.check("verification", "work_visibility", "FAIL", "blocking", evidence)

    def run_installed_qa_support(self) -> None:
        script_path = PLUGIN_ROOT / "scripts" / "installed_runtime_qa.py"
        if not script_path.exists():
            self.check("verification", "installed_qa_support", "FAIL", "blocking", "installed_runtime_qa.py not found")
            return
        ok, evidence = self.syntax_ok(script_path)
        if ok:
            self.check("verification", "installed_qa_support", "PASS", "info", "installed runtime QA receipt script parses")
        else:
            self.check("verification", "installed_qa_support", "FAIL", "blocking", evidence[:240])

    def run_product_intake(self) -> None:
        ok, evidence = product_intake.smoke_check()
        if ok:
            self.check("verification", "product_intake_smoke", "PASS", "info", evidence)
        else:
            self.check("verification", "product_intake_smoke", "FAIL", "blocking", evidence)

    def run_front_door(self) -> None:
        ok, evidence = front_door.smoke_check()
        if ok:
            self.check("verification", "front_door_smoke", "PASS", "info", evidence)
        else:
            self.check("verification", "front_door_smoke", "FAIL", "blocking", evidence)

    def run_command_guard(self) -> None:
        assessment = front_door.assess_command_guidance(
            "npm test || git status",
            {"os": "windows", "shell": "powershell"},
        )
        required = {
            "powershell-npm-ps1",
            "powershell-bash-or",
            "git-root-required",
        }
        guard = assessment.get("command_guard", {})
        if (
            not assessment.get("safe")
            and required.issubset(set(assessment.get("violations", [])))
            and guard.get("package_runner") == "npm.cmd"
            and guard.get("cwd_rule") == "resolve-repo-root-before-git"
        ):
            self.check(
                "verification",
                "command_guard",
                "PASS",
                "info",
                "Windows guard covers npm.cmd, PowerShell operators, and Git repo root",
            )
        else:
            self.check(
                "verification",
                "command_guard",
                "FAIL",
                "blocking",
                "Windows command guard missing or incomplete",
            )

    def run_memory_preflight(self) -> None:
        ok, evidence = memory_preflight.smoke_check()
        if ok:
            self.check("memory", "memory_preflight", "PASS", "info", evidence)
        else:
            self.check("memory", "memory_preflight", "FAIL", "blocking", evidence)

    def run_status_model(self) -> None:
        ok, evidence = status_model.smoke_check()
        if ok:
            self.check("verification", "status_model_smoke", "PASS", "info", evidence)
        else:
            self.check("verification", "status_model_smoke", "FAIL", "blocking", evidence)

    def run_runtime_truth(self) -> None:
        info = runtime_info.build_runtime_info(PROJECT_ROOT, PLUGIN_ROOT)
        source_root = info.get("plugin_source_root")
        runtime_root = info.get("installed_plugin_root")
        source_version = info.get("plugin_source_version")
        runtime_version = info.get("installed_runtime_version")
        project_version = info.get("project_state_version")

        if source_root:
            self.check("runtime", "source_root", "PASS", "info", source_root)
        else:
            self.check("runtime", "source_root", "WARN", "warning", "No source plugin root found from marketplace")

        if info.get("marketplace_root"):
            self.check("runtime", "marketplace_root", "PASS", "info", str(info["marketplace_root"]))
        else:
            self.check("runtime", "marketplace_root", "WARN", "warning", "No marketplace root found")

        if info.get("marketplace_name"):
            if info.get("managed_marketplace_configured"):
                mode = info.get("marketplace_upgrade_mode")
                source = info.get("managed_marketplace_source") or "unknown source"
                if mode == "git":
                    evidence = f"{info['marketplace_name']} tracked as Git marketplace: {source}"
                else:
                    evidence = f"{info['marketplace_name']} tracked as local marketplace: {source}"
                self.check("runtime", "managed_marketplace", "PASS", "info", evidence)
            else:
                command = f"codex plugin marketplace add \"{info.get('marketplace_root')}\""
                self.check("runtime", "managed_marketplace", "WARN", "warning", f"Not in Codex managed marketplace list. Add: {command}")

        if runtime_root:
            self.check("runtime", "installed_root", "PASS", "info", runtime_root)
        else:
            self.check(
                "runtime",
                "installed_root",
                "WARN",
                "warning",
                self.plain_next(
                    "No installed runtime found in Codex cache.",
                    "install or refresh ACC in Codex, then open a new thread.",
                ),
            )

        if runtime_root:
            runtime_path = Path(str(runtime_root))
            installed_doctor = runtime_path / "scripts" / "doctor.py"
            installed_manifest = runtime_path / ".codex-plugin" / "plugin.json"
            if installed_doctor.exists() and installed_manifest.exists():
                self.check("runtime", "installed_source", "PASS", "info", "Installed ACC source has manifest and Doctor")
            else:
                self.check(
                    "runtime",
                    "installed_source",
                    "WARN",
                    "warning",
                    self.plain_next(
                        "Installed ACC runtime is incomplete.",
                        "refresh ACC from its marketplace source; do not edit another plugin.",
                    ),
                )
        else:
            self.check(
                "runtime",
                "installed_source",
                "WARN",
                "warning",
                self.plain_next(
                    "Installed ACC source cannot be checked because runtime is missing.",
                    "install or refresh ACC in Codex first.",
                ),
            )

        if source_version and runtime_version:
            if runtime_info.compare_versions(source_version, runtime_version) == 0:
                self.check("runtime", "source_runtime_match", "PASS", "info", f"{source_version} == {runtime_version}")
            else:
                self.check(
                    "runtime",
                    "source_runtime_match",
                    "WARN",
                    "warning",
                    self.plain_next(
                        f"source {source_version}, runtime {runtime_version}.",
                        "refresh ACC through Codex, restart, then rerun Doctor.",
                    ),
                )

        if project_version and runtime_version:
            if runtime_info.compare_versions(project_version, runtime_version) == 0:
                self.check("runtime", "project_runtime_match", "PASS", "info", f"{project_version} == {runtime_version}")
            else:
                self.check(
                    "runtime",
                    "project_runtime_match",
                    "WARN",
                    "warning",
                    self.plain_next(
                        f"project {project_version}, runtime {runtime_version}.",
                        "run update only after ACC runtime is refreshed.",
                    ),
                )

        if info.get("wrong_root_hint"):
            self.check("runtime", "project_root_hint", "WARN", "warning", f"Maybe wrong root. Try: {info['wrong_root_hint']}")
        elif PROJECT_ROOT.name.lower() == "codex":
            self.check("runtime", "project_root_hint", "WARN", "warning", "Looks like umbrella root, not plugin-dev repo")
        else:
            self.check("runtime", "project_root_hint", "PASS", "info", str(PROJECT_ROOT))

    def run_plugin_conflicts(self) -> None:
        plugins = front_door.scan_installed_plugins()
        duplicate_note = ""
        acc_entries = [
            (
                plugin.get("manifest"),
                runtime_info.read_manifest_version(Path(str(plugin.get("manifest", ""))).parent.parent),
            )
            for plugin in plugins
            if front_door.normalize_text(plugin.get("name")) == PROJECT_NAMESPACE
        ]
        if len(acc_entries) > 1:
            versions = [version for _, version in acc_entries]
            first = versions[0]
            same_version = bool(first) and all(
                runtime_info.compare_versions(first, version) == 0
                for version in versions
                if version
            ) and all(versions)
            if same_version:
                duplicate_note = f"{len(acc_entries)} ACC cache entries share version {first}; runtime selector owns active source. "
            else:
                self.check(
                    "runtime",
                    "plugin_conflicts",
                    "WARN",
                    "warning",
                    self.plain_next(
                        f"Multiple installed ACC runtimes found: {len(acc_entries)}.",
                        "refresh ACC from one marketplace source; do not edit other plugins.",
                    ),
                )
                return

        possible_owners = []
        for plugin in plugins:
            name = front_door.normalize_text(plugin.get("name"))
            if not name or name == PROJECT_NAMESPACE:
                continue
            capability_text = front_door.normalize_text(plugin.get("capability_text"))
            if any(word in capability_text for word in WORKFLOW_CONTROL_WORDS):
                possible_owners.append(name)

        if possible_owners:
            self.check(
                "runtime",
                "plugin_conflicts",
                "PASS",
                "info",
                self.plain_next(
                    f"{duplicate_note}Possible workflow helpers present: {', '.join(sorted(possible_owners))}. ACC keeps workflow ownership and fallback.",
                    "ask before handing ownership to another plugin.",
                ),
            )
        else:
            self.check(
                "runtime",
                "plugin_conflicts",
                "PASS",
                "info",
                f"{duplicate_note}ACC owns workflow; other plugins stay bounded helpers.",
            )

    def summary(self) -> dict:
        summary = {"pass": 0, "warn": 0, "fail": 0}
        for item in self.results:
            if item["status"] == "PASS":
                summary["pass"] += 1
            elif item["status"] == "WARN":
                summary["warn"] += 1
            elif item["status"] == "FAIL":
                summary["fail"] += 1
        return summary

    def run_plugin_cache(self, cache_root: Path | None = None) -> None:
        """Detect stale duplicate cache versions and skills missing from cache.

        Real-trial failure: two versions cached at once, orchestrator skill
        vanished mid-session and the workflow drifted to other plugins.
        """
        if cache_root is None:
            cache_root = Path.home() / ".codex" / "plugins" / "cache"
        plugin_dirs = list(cache_root.glob("*/anyone-can-code")) if cache_root.exists() else []
        version_dirs = [
            version
            for plugin_dir in plugin_dirs
            for version in plugin_dir.iterdir()
            if version.is_dir()
        ]
        if not version_dirs:
            self.check(
                "config", "plugin_cache_versions", "PASS", "info",
                "No installed plugin cache found (normal on dev machine)",
            )
            return

        if len(version_dirs) > 1:
            names = ", ".join(sorted(v.name for v in version_dirs))
            self.check(
                "config", "plugin_cache_versions", "WARN", "warning",
                f"Multiple cached versions live at once: {names}. "
                "Remove stale ones; duplicates caused skill loss in real use.",
            )
        else:
            self.check(
                "config", "plugin_cache_versions", "PASS", "info",
                f"Single cached version: {version_dirs[0].name}",
            )

        expected = {
            p.name for p in (PLUGIN_ROOT / "skills").iterdir() if p.is_dir()
        } if (PLUGIN_ROOT / "skills").exists() else set()
        newest = max(version_dirs, key=lambda v: v.stat().st_mtime)
        cached = {
            p.name for p in (newest / "skills").iterdir() if p.is_dir()
        } if (newest / "skills").exists() else set()
        missing = sorted(expected - cached)
        if missing:
            self.check(
                "config", "plugin_cache_skills", "FAIL", "blocking",
                f"Cache {newest.name} missing skills: {', '.join(missing)}. "
                "Reinstall/upgrade the plugin from marketplace.",
            )
        else:
            self.check(
                "config", "plugin_cache_skills", "PASS", "info",
                f"All {len(expected)} skills present in cache {newest.name}",
            )

    def run_token_budget(self) -> None:
        """Plugin's own text is a per-session token tax; keep it caveman-small."""
        results = run_skill_budget()
        over = [r for r in results if r["status"] == "FAIL"]
        if over:
            self.check(
                "skills", "skill_token_budget", "FAIL", "blocking",
                "Skill docs over budget: " + "; ".join(r["detail"] for r in over),
            )
        else:
            self.check(
                "skills", "skill_token_budget", "PASS", "info",
                f"All {len(results)} skill docs within {SKILL_BUDGET_CHARS} chars",
            )

    def run_all(self) -> dict:
        global PROJECT_ROOT
        requested_root = PROJECT_ROOT
        selection = runtime_info.resolve_acc_project(requested_root)
        self.run_project_selection(selection)
        if selection["status"] == "selected":
            PROJECT_ROOT = Path(selection["project_root"])
        self.run_python()
        try:
            self.run_manifest()
            self.run_hooks_bundle()
            self.run_hook_scripts()
            self.run_skills()
            self.run_mcp()
            self.run_project_layout()
            self.run_project_state()
            self.run_project_config()
            self.run_hook_health()
            self.run_default_prompts()
            self.run_usage_script()
            self.run_work_visibility()
            self.run_installed_qa_support()
            self.run_product_intake()
            self.run_front_door()
            self.run_command_guard()
            self.run_memory_preflight()
            self.run_status_model()
            self.run_runtime_truth()
            self.run_plugin_conflicts()
            self.run_plugin_cache()
            self.run_token_budget()
            return {"results": self.results, "summary": self.summary()}
        finally:
            PROJECT_ROOT = requested_root


def main() -> None:
    global PROJECT_ROOT
    parser = argparse.ArgumentParser(description="Anyone Can Code doctor")
    parser.add_argument("target", nargs="?", default=None,
                        help="Project root to check (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.target:
        target_path = Path(args.target).expanduser()
        if not target_path.is_dir():
            reason = "not found" if not target_path.exists() else "not a directory"
            print(f"doctor: target {reason}: {target_path}", file=sys.stderr)
            sys.exit(2)
        PROJECT_ROOT = target_path

    doctor = Doctor(json_mode=args.json)
    report = doctor.run_all()
    if args.json:
        print(json.dumps(report, indent=2))
        return
    summary = report["summary"]
    print(f"Doctor: {summary['pass']} PASS, {summary['warn']} WARN, {summary['fail']} FAIL")


if __name__ == "__main__":
    main()
