from __future__ import annotations

import json
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"acc_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_hook_script(name: str):
    path = PLUGIN_ROOT / "hooks" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"acc_hook_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


setup = load_script("setup")
doctor = load_script("doctor")
update = load_script("update")
save_session = load_hook_script("save_session")
hook_state = load_hook_script("state")
guard = load_hook_script("guard")
canonical_state = load_script("canonical_state")
task_coordination = load_script("task_coordination")
safety_receipts = load_script("safety_receipts")
work_visibility = load_script("work_visibility")
installed_runtime_qa = load_script("installed_runtime_qa")


class ProjectStateTests(unittest.TestCase):
    def test_project_resolver_selects_one_active_nested_project_over_idle_root(self) -> None:
        resolver = getattr(doctor.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup.bootstrap_project(root)
            nested = root / "zenfit-site"
            setup.bootstrap_project(nested)
            workflow_path = (
                nested / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["active_task_capsule"] = {
                "goal": "Refine Zenfit",
                "task": "Polish existing website",
                "next_action": "Continue implementation",
            }
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            result = resolver(root)

        self.assertEqual(result["status"], "selected")
        self.assertEqual(Path(result["project_root"]), nested.resolve())
        self.assertEqual(result["reason"], "single-meaningful-nested-project")

    def test_project_resolver_keeps_meaningfully_active_root(self) -> None:
        resolver = getattr(doctor.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup.bootstrap_project(root)
            workflow_path = root / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["next_step"] = "Run tests"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")
            setup.bootstrap_project(root / "idle-child")

            result = resolver(root)

        self.assertEqual(result["status"], "selected")
        self.assertEqual(Path(result["project_root"]), root.resolve())
        self.assertEqual(result["reason"], "requested-root-meaningful")

    def test_project_resolver_blocks_multiple_meaningful_projects(self) -> None:
        resolver = getattr(doctor.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("site-one", "site-two"):
                candidate = root / name
                setup.bootstrap_project(candidate)
                workflow_path = (
                    candidate / ".codex" / "anyone-can-code" / "state" / "workflow.json"
                )
                workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
                workflow["phase"] = "build"
                workflow["next_step"] = f"Continue {name}"
                workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            result = resolver(root)

        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["candidates"]), 2)
        self.assertIsNone(result["project_root"])

    def test_project_resolver_ignores_generated_folders(self) -> None:
        resolver = getattr(doctor.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "node_modules" / "copied-project"
            setup.bootstrap_project(generated)

            result = resolver(root)

        self.assertEqual(result["status"], "selected")
        self.assertEqual(Path(result["project_root"]), root.resolve())
        self.assertEqual(result["candidates"], [])

    def test_project_resolver_ignores_worktree_containers(self) -> None:
        resolver = getattr(doctor.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup.bootstrap_project(root)
            workflow_path = root / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["next_step"] = "Continue root"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            worktree = root / ".worktrees" / "dev-copy"
            setup.bootstrap_project(worktree)
            copied_workflow_path = (
                worktree / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            copied_workflow = json.loads(copied_workflow_path.read_text(encoding="utf-8"))
            copied_workflow["phase"] = "build"
            copied_workflow["next_step"] = "Copied state"
            copied_workflow_path.write_text(json.dumps(copied_workflow), encoding="utf-8")

            result = resolver(root)

        self.assertEqual(result["status"], "selected")
        self.assertEqual(Path(result["project_root"]), root.resolve())
        self.assertEqual(result["reason"], "requested-root-meaningful")

    def test_setup_resolves_nested_project_before_writing_root_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "zenfit-site"
            setup.bootstrap_project(nested)
            workflow_path = (
                nested / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["next_step"] = "Continue Zenfit"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            receipt = setup.bootstrap_project(root)

        self.assertFalse((root / ".codex" / "anyone-can-code").exists())
        self.assertEqual(Path(receipt["project_root"]), nested.resolve())

    def test_setup_blocks_ambiguous_nested_projects_before_writing_root_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("site-one", "site-two"):
                candidate = root / name
                setup.bootstrap_project(candidate)
                workflow_path = (
                    candidate / ".codex" / "anyone-can-code" / "state" / "workflow.json"
                )
                workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
                workflow["phase"] = "build"
                workflow["next_step"] = f"Continue {name}"
                workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Multiple ACC projects"):
                setup.bootstrap_project(root)

        self.assertFalse((root / ".codex" / "anyone-can-code").exists())

    def test_update_resolves_nested_project_before_loading_install_state(self) -> None:
        resolver = getattr(update.runtime_info, "resolve_acc_project", None)
        self.assertIsNotNone(resolver)
        if resolver is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "zenfit-site"
            setup.bootstrap_project(nested)
            workflow_path = (
                nested / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["next_step"] = "Continue Zenfit"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            with (
                mock.patch.object(update, "load_install_state", wraps=update.load_install_state) as load,
                mock.patch.object(
                    update.runtime_info,
                    "build_runtime_info",
                    return_value={
                        "plugin_source_version": "1.0.0",
                        "installed_runtime_version": "1.0.0",
                        "project_root": str(nested),
                        "next_action": "same-everywhere",
                    },
                ),
            ):
                update.migrate(root)

        self.assertEqual(load.call_args.args[0], nested.resolve())

    def test_help_status_and_resume_require_project_resolution(self) -> None:
        for skill in ("help", "status", "resume"):
            with self.subTest(skill=skill):
                text = (
                    PLUGIN_ROOT / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("--resolve-project", text)
                self.assertIn("ambiguous", text.lower())

    def test_doctor_reports_and_uses_selected_nested_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup.bootstrap_project(root)
            nested = root / "zenfit-site"
            setup.bootstrap_project(nested)
            workflow_path = (
                nested / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["phase"] = "build"
            workflow["next_step"] = "Continue Zenfit"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = root
            try:
                report = doctor.Doctor(json_mode=True).run_all()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in report["results"]}
        self.assertEqual(by_check["project_selection"]["status"], "WARN")
        self.assertIn(str(nested.resolve()), by_check["project_selection"]["evidence"])
        self.assertEqual(by_check["workflow_state"]["status"], "PASS")

    def test_usage_budget_estimates_large_reads_and_loops_with_uncertainty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            large_file = target / "large.txt"
            large_file.write_text("x" * 26000, encoding="utf-8")

            budget = work_visibility.estimate_context_cost(
                paths=[large_file],
                loop_items=40,
            )

        self.assertTrue(budget["large_read"])
        self.assertTrue(budget["large_loop"])
        self.assertIn("exact usage may differ", budget["uncertainty"])
        self.assertGreaterEqual(len(budget["warnings"]), 2)

    def test_high_usage_checkpoint_thresholds_force_split_before_burn(self) -> None:
        normal = work_visibility.assess_usage_checkpoint(primary_percent=84)
        checkpoint = work_visibility.assess_usage_checkpoint(primary_percent=85)
        split = work_visibility.assess_usage_checkpoint(primary_percent=90)
        stop = work_visibility.assess_usage_checkpoint(primary_percent=94)

        self.assertEqual(normal["action"], "continue")
        self.assertFalse(normal["checkpoint_required"])
        self.assertEqual(checkpoint["action"], "checkpoint")
        self.assertTrue(checkpoint["checkpoint_required"])
        self.assertFalse(checkpoint["continue_without_user_choice"])
        self.assertEqual(split["action"], "split")
        self.assertTrue(split["split_required"])
        self.assertFalse(split["continue_without_user_choice"])
        self.assertEqual(stop["action"], "stop-now")
        self.assertTrue(stop["stop_required"])
        self.assertFalse(stop["continue_without_user_choice"])
        self.assertIn("reported percentage", stop["uncertainty"])

    def test_patch_retry_requires_exact_reread_after_failed_patch(self) -> None:
        first = work_visibility.assess_patch_retry(
            failed_attempts=0,
            last_patch_failed=False,
            exact_target_reread=False,
        )
        blocked = work_visibility.assess_patch_retry(
            failed_attempts=1,
            last_patch_failed=True,
            exact_target_reread=False,
        )
        retry = work_visibility.assess_patch_retry(
            failed_attempts=1,
            last_patch_failed=True,
            exact_target_reread=True,
        )
        exhausted = work_visibility.assess_patch_retry(
            failed_attempts=2,
            last_patch_failed=True,
            exact_target_reread=True,
        )

        self.assertTrue(first["can_apply_patch"])
        self.assertEqual(first["action"], "apply")
        self.assertFalse(blocked["can_apply_patch"])
        self.assertEqual(blocked["action"], "reread-exact-target")
        self.assertTrue(blocked["reread_required"])
        self.assertTrue(retry["can_apply_patch"])
        self.assertEqual(retry["action"], "retry-once")
        self.assertFalse(exhausted["can_apply_patch"])
        self.assertEqual(exhausted["action"], "stop-and-replan")

    def test_docs_first_mechanics_gate_blocks_platform_work_without_brief(self) -> None:
        normal = work_visibility.assess_mechanics_docs_gate(
            "Add password reset to the existing app",
        )
        blocked = work_visibility.assess_mechanics_docs_gate(
            "Change Codex Desktop hook launch behavior on Windows",
        )
        documented = work_visibility.assess_mechanics_docs_gate(
            "Change Codex Desktop hook launch behavior on Windows",
            docs_brief="Official docs and source checked; hook launch boundary recorded.",
        )
        controlled = work_visibility.assess_mechanics_docs_gate(
            "Change telemetry parsing for Codex Desktop logs",
            controlled_proof=True,
            uncertainty="Official docs missing; controlled log fixture proves only this boundary.",
        )

        self.assertTrue(normal["can_change_code"])
        self.assertFalse(normal["docs_brief_required"])
        self.assertFalse(blocked["can_change_code"])
        self.assertTrue(blocked["docs_brief_required"])
        self.assertEqual(blocked["action"], "write-docs-brief")
        self.assertTrue(documented["can_change_code"])
        self.assertEqual(documented["evidence_source"], "docs-brief")
        self.assertTrue(controlled["can_change_code"])
        self.assertEqual(controlled["evidence_source"], "controlled-proof-with-uncertainty")

    def test_tool_evidence_receipt_compacts_large_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            receipt = work_visibility.write_tool_evidence_receipt(
                target,
                tool="Bash",
                command="test command",
                exit_code=0,
                stdout="A" * 3000,
            )
            text = Path(receipt["receipt_markdown"]).read_text(encoding="utf-8")

        self.assertTrue(receipt["evidence"]["compacted"])
        self.assertIn("Compacted: yes", text)
        self.assertLess(len(receipt["evidence"]["excerpt"]), 2000)

    def test_background_work_must_be_visible_stoppable_and_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            blocked = work_visibility.start_background_work(
                target,
                name="bad scanner",
                purpose="",
                stop_command="",
                stopping_condition="",
                limit_seconds=0,
                limit_steps=0,
            )
            started = work_visibility.start_background_work(
                target,
                name="session scan",
                purpose="scan local Codex sessions for usage",
                stop_command="python scripts/codeburn.py stop",
                stopping_condition="stop after one scan or 60 seconds",
                limit_seconds=60,
                limit_steps=1,
            )
            completed = work_visibility.complete_background_work(
                target,
                started["id"],
                status="completed",
                evidence=["one scan complete"],
            )

        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("purpose", blocked["work"]["missing"])
        self.assertEqual(started["status"], "started")
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["work"]["state"], "completed")

    def test_normal_work_uses_cheap_checks_and_risk_uses_deep_checks(self) -> None:
        cheap = work_visibility.choose_check_depth(changed_files=1)
        deep = work_visibility.choose_check_depth(
            changed_files=2,
            shared_behavior=True,
            user_visible=True,
        )

        self.assertEqual(cheap["depth"], "cheap")
        self.assertNotIn("full tests", cheap["checks"])
        self.assertEqual(deep["depth"], "deep")
        self.assertIn("doctor", deep["checks"])

    def test_installed_runtime_qa_fails_when_target_is_not_installed_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / "source-copy"
            runtime.mkdir()

            receipt = installed_runtime_qa.run_installed_qa(
                target,
                PLUGIN_ROOT,
                runtime_root=runtime,
            )

        self.assertEqual(receipt["status"], "fail")
        self.assertIn("not Codex installed cache", receipt["plain_result"])

    def test_installed_runtime_qa_does_not_false_pass_missing_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / ".codex" / "plugins" / "cache" / "market" / "anyone-can-code" / "1.0.0"
            (runtime / "skills" / "setup").mkdir(parents=True)
            (runtime / "skills" / "setup" / "SKILL.md").write_text(
                "Use `$setup` after the plugin is installed\n",
                encoding="utf-8",
            )

            receipt = installed_runtime_qa.run_installed_qa(
                target,
                PLUGIN_ROOT,
                runtime_root=runtime,
            )

        self.assertEqual(receipt["status"], "fail")
        self.assertIn("failed", receipt["plain_result"])
        self.assertTrue(any(item["status"] == "fail" for item in receipt["scenarios"]))

    def test_installed_runtime_qa_proves_memory_write_through(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / ".codex" / "plugins" / "cache" / "market" / "anyone-can-code" / "1.0.0"
            shutil.copytree(PLUGIN_ROOT, runtime)

            receipt = installed_runtime_qa.run_installed_qa(
                target,
                PLUGIN_ROOT,
                runtime_root=runtime,
            )

        scenarios = {item["id"]: item for item in receipt["scenarios"]}
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(scenarios["memory_write_through"]["status"], "pass")
        self.assertIn("setup", scenarios["memory_write_through"]["proof"])
        self.assertIn("update", scenarios["memory_write_through"]["proof"])
        self.assertIn("new-thread", scenarios["memory_write_through"]["proof"])

    def test_installed_runtime_qa_proves_visible_response_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / ".codex" / "plugins" / "cache" / "market" / "anyone-can-code" / "1.0.0"
            shutil.copytree(PLUGIN_ROOT, runtime)

            receipt = installed_runtime_qa.run_installed_qa(
                target,
                PLUGIN_ROOT,
                runtime_root=runtime,
            )

        scenarios = {item["id"]: item for item in receipt["scenarios"]}
        visible = scenarios["visible_response_contract"]
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(visible["status"], "pass")
        self.assertIn("existing-website-route", visible["proof"])
        self.assertIn("visible-text-required", visible["proof"])
        self.assertIn("acc-fallback-response", visible["proof"])
        self.assertIn("rendered-message", visible["proof"])
        self.assertGreater(len(visible["details"]["displayed_text"]), 20)

    def test_installed_runtime_qa_proves_nested_hook_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / ".codex" / "plugins" / "cache" / "market" / "anyone-can-code" / "1.0.0"
            shutil.copytree(PLUGIN_ROOT, runtime)

            receipt = installed_runtime_qa.run_installed_qa(
                target,
                PLUGIN_ROOT,
                runtime_root=runtime,
            )

        scenarios = {item["id"]: item for item in receipt["scenarios"]}
        hooks = scenarios["hook_nested_root_receipts"]
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(hooks["status"], "pass")
        self.assertIn("nested-resolution", hooks["proof"])
        self.assertIn("useful-context", hooks["proof"])
        self.assertIn("durable-receipt", hooks["proof"])
        self.assertIn("stop-state-write", hooks["proof"])
        self.assertIn("ambiguous-skip-clean", hooks["proof"])
        self.assertIn("bare-skip-clean", hooks["proof"])
        self.assertIn("redacted-prompt", hooks["proof"])
        self.assertIn(".codex/anyone-can-code/state/turn-ledger.jsonl", hooks["details"]["stop_state_paths"])

    def test_task_coordination_records_ownership_claims_dependencies_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            task_coordination.set_task_queue(
                target,
                [
                    {"id": "design", "name": "Design flow", "status": "done", "evidence": ["Sketch approved"]},
                    {"id": "build", "name": "Build flow", "dependencies": ["design"], "owner": "acc"},
                ],
            )

            claimed = task_coordination.claim_task(
                target,
                "build",
                owner="acc",
                claim_id="claim-1",
            )
            with self.assertRaises(task_coordination.TaskCoordinationError):
                task_coordination.claim_task(
                    target,
                    "build",
                    owner="other-worker",
                    claim_id="claim-2",
                )
            completed = task_coordination.complete_task(
                target,
                "build",
                claim_id="claim-1",
                evidence=["72 tests passed"],
            )

        by_id = {task["id"]: task for task in completed["tasks"]}
        self.assertEqual(claimed["task_claims"]["build"]["claim_id"], "claim-1")
        self.assertEqual(by_id["build"]["status"], "done")
        self.assertEqual(by_id["build"]["owner"], "acc")
        self.assertEqual(by_id["build"]["dependencies"], ["design"])
        self.assertIn("72 tests passed", by_id["build"]["evidence"])
        self.assertNotIn("build", completed["task_claims"])

    def test_subagent_assignment_requires_user_request_and_codex_need(self) -> None:
        denied_user = task_coordination.build_subagent_assignment(
            task="Parallel QA",
            user_requested=False,
            codex_requires_subagent=True,
            reason="Needs isolated context",
        )
        denied_need = task_coordination.build_subagent_assignment(
            task="Parallel QA",
            user_requested=True,
            codex_requires_subagent=False,
            reason="Can run inline",
        )
        approved = task_coordination.build_subagent_assignment(
            task="Parallel QA",
            user_requested=True,
            codex_requires_subagent=True,
            reason="Needs isolated context",
            max_parallel=3,
        )

        self.assertFalse(denied_user["approved"])
        self.assertEqual(denied_user["reason"], "explicit-user-request-required")
        self.assertFalse(denied_need["approved"])
        self.assertEqual(denied_need["reason"], "codex-subagent-need-not-present")
        self.assertTrue(approved["approved"])
        self.assertEqual(approved["workflow_owner"], "acc")
        self.assertEqual(approved["bounds"]["return_to"], "acc")
        self.assertEqual(approved["bounds"]["max_parallel"], 3)

    def test_hook_health_records_one_purpose_per_hook_and_opens_circuit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for hook_name in ("guard", "audit", "load_session", "save_session"):
                hook_state.record_hook_result(target, hook_name, "pass")

            hook_state.record_hook_result(target, "guard", "fail", reason="boom")
            open_entry = hook_state.record_hook_result(target, "guard", "fail", reason="boom again")
            called = False

            def worker() -> dict:
                nonlocal called
                called = True
                return {"should": "not run"}

            result = hook_state.run_optional_hook(target, "guard", worker)
            health = hook_state.read_hook_health(target)

        purposes = {
            name: entry["purpose"]
            for name, entry in health["hooks"].items()
            if name in {"guard", "audit", "load_session", "save_session"}
        }
        self.assertEqual(set(purposes), {"guard", "audit", "load_session", "save_session"})
        self.assertTrue(all(purposes.values()))
        self.assertTrue(open_entry["circuit_open"])
        self.assertFalse(called)
        self.assertEqual(result, {})

    def test_optional_hook_failure_returns_empty_result_and_records_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            result = hook_state.run_optional_hook(
                target,
                "save_session",
                lambda: (_ for _ in ()).throw(RuntimeError("write failed")),
            )
            health = hook_state.read_hook_health(target)

        self.assertEqual(result, {})
        self.assertEqual(health["hooks"]["save_session"]["status"], "fail")
        self.assertEqual(health["hooks"]["save_session"]["consecutive_failures"], 1)

    def test_hooks_skip_when_acc_not_setup_even_if_git_exists(self) -> None:
        """Hooks must not run (or create ACC state) until $setup made the project."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "bare-repo"
            (repo / ".git").mkdir(parents=True)
            payload = {
                "hook_event_name": "SessionStart",
                "session_id": "s-bare",
                "cwd": str(repo),
            }

            resolution = hook_state.resolve_hook_project(payload)
            result = hook_state.run_hook_attempt(
                resolution,
                "load_session",
                payload,
                lambda: {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "should not inject",
                    }
                },
            )
            acc_root = repo / ".codex" / "anyone-can-code"

        self.assertEqual(resolution["status"], "unresolved")
        self.assertEqual(resolution["reason"], "no-project")
        self.assertEqual(result, {})
        self.assertFalse(acc_root.exists())

    def test_hook_finds_nested_acc_under_bare_git_monorepo(self) -> None:
        """Monorepo git root without ACC still finds one nested ACC-setup child."""
        with tempfile.TemporaryDirectory() as tmp:
            mono = Path(tmp) / "mono"
            (mono / ".git").mkdir(parents=True)
            nested = mono / "app"
            nested.mkdir()
            hook_state.ensure_project_layout(nested)
            payload = {"hook_event_name": "SessionStart", "cwd": str(mono)}

            resolution = hook_state.resolve_hook_project(payload)

        self.assertEqual(resolution["status"], "resolved")
        self.assertEqual(Path(resolution["project_root"]), nested.resolve())

    def test_hook_resolver_selects_single_nested_project_from_non_git_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            nested = workspace / "zenfit-site"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {
                "hook_event_name": "SessionStart",
                "session_id": "s1",
                "cwd": str(workspace),
            }

            resolution = hook_state.resolve_hook_project(payload)
            result = hook_state.run_hook_attempt(
                resolution,
                "load_session",
                payload,
                lambda: {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "Talk: caveman-strict.",
                    }
                },
            )
            receipt = json.loads(
                (
                    nested
                    / ".codex"
                    / "anyone-can-code"
                    / "logs"
                    / "hook-receipts.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )

        self.assertEqual(resolution["status"], "resolved")
        self.assertEqual(Path(resolution["project_root"]), nested.resolve())
        self.assertIn("hookSpecificOutput", result)
        self.assertEqual(receipt["resolution_state"], "resolved")
        self.assertEqual(receipt["chosen_project"], str(nested.resolve()))
        self.assertTrue(receipt["context_returned"])
        self.assertEqual(receipt["final_effectiveness"], "useful")

    def test_hook_skips_when_project_root_is_ambiguous(self) -> None:
        # D-039/D-044: ambiguous project cannot be chosen silently; hook skips.
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            first = workspace / "first"
            second = workspace / "second"
            for candidate in (first, second):
                (candidate / ".git").mkdir(parents=True)
                hook_state.ensure_project_layout(candidate)
            payload = {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "build this",
                "cwd": str(workspace),
            }

            resolution = hook_state.resolve_hook_project(payload)
            result = hook_state.run_hook_attempt(
                resolution,
                "guard",
                payload,
                lambda: {"ran": True},
            )
            # No chosen ACC project → no receipt writes (must not create ACC on parent).
            parent_layout = workspace / ".codex" / "anyone-can-code"

        self.assertEqual(result, {})
        self.assertEqual(resolution["status"], "ambiguous")
        self.assertEqual(len(resolution["candidates"]), 2)
        self.assertFalse(parent_layout.exists())

    def test_save_session_skips_when_project_root_is_ambiguous(self) -> None:
        # D-039/D-044: ambiguous project cannot be chosen silently; hook skips.
        # Orchestrator must surface ambiguity to user before any state is written.
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            first = workspace / "first"
            second = workspace / "second"
            for candidate in (first, second):
                (candidate / ".git").mkdir(parents=True)
                hook_state.ensure_project_layout(candidate)
            payload = {
                "hook_event_name": "Stop",
                "cwd": str(workspace),
            }

            with mock.patch.object(hook_state, "git_root_from_ancestors", return_value=None):
                resolution = hook_state.resolve_hook_project(payload)
            result = hook_state.run_hook_attempt(
                resolution,
                "save_session",
                payload,
                lambda: hook_state.write_state(
                    Path(str(resolution.get("cwd"))),
                    {"phase": "build", "route": "fallback"},
                ),
            )
            workflow_path = workspace / ".codex" / "anyone-can-code" / "state" / "workflow.json"

        self.assertEqual(resolution["status"], "ambiguous")
        self.assertEqual(result, {})
        self.assertFalse(workflow_path.exists())

    def test_guard_prompt_submit_does_not_run_routing_or_write_workflow_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            payload = {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "fix the failing build",
                "turn_id": "turn-1",
            }

            with (
                mock.patch.object(guard.state, "detect_phase", side_effect=AssertionError),
                mock.patch.object(guard.state, "detect_entry_mode", side_effect=AssertionError),
                mock.patch.object(guard.state, "write_state", side_effect=AssertionError),
            ):
                result = guard.handle_payload(payload, target)

            workflow_path = target / ".codex" / "anyone-can-code" / "state" / "workflow.json"

        self.assertIn("hookSpecificOutput", result)
        self.assertFalse(workflow_path.exists())

    def test_hook_receipt_classifies_empty_output_as_noop_not_useful(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {"hook_event_name": "PreToolUse", "cwd": str(nested)}

            resolution = hook_state.resolve_hook_project(payload)
            result = hook_state.run_hook_attempt(
                resolution,
                "guard",
                payload,
                lambda: {},
            )
            receipt = json.loads(
                (
                    nested
                    / ".codex"
                    / "anyone-can-code"
                    / "logs"
                    / "hook-receipts.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )

        self.assertEqual(result, {})
        self.assertEqual(receipt["output_kind"], "empty")
        self.assertFalse(receipt["context_returned"])
        self.assertEqual(receipt["final_effectiveness"], "no-op")

    def test_run_hook_attempt_pretooluse_worker_crash_fails_closed(self) -> None:
        """Docs: exit 0 empty continues tool — crash must return PreToolUse deny."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {"hook_event_name": "PreToolUse", "cwd": str(nested)}
            resolution = hook_state.resolve_hook_project(payload)

            result = hook_state.run_hook_attempt(
                resolution,
                "guard",
                payload,
                lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            )
            receipt = json.loads(
                (
                    nested
                    / ".codex"
                    / "anyone-can-code"
                    / "logs"
                    / "hook-receipts.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )

        specific = result.get("hookSpecificOutput") or {}
        self.assertEqual(specific.get("hookEventName"), "PreToolUse")
        self.assertEqual(specific.get("permissionDecision"), "deny")
        self.assertIn("Blocked for safety", specific.get("permissionDecisionReason", ""))
        self.assertEqual(receipt["failure_class"], "RuntimeError")
        self.assertEqual(receipt["exit_status"], "failure")
        self.assertEqual(receipt["final_effectiveness"], "failed")

    def test_run_hook_attempt_permission_request_worker_crash_fails_closed(self) -> None:
        """Docs: PermissionRequest deny shape; empty would skip to normal approval."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {"hook_event_name": "PermissionRequest", "cwd": str(nested)}
            resolution = hook_state.resolve_hook_project(payload)

            result = hook_state.run_hook_attempt(
                resolution,
                "audit",
                payload,
                lambda: (_ for _ in ()).throw(ValueError("gate broke")),
            )

        decision = (result.get("hookSpecificOutput") or {}).get("decision") or {}
        self.assertEqual((result.get("hookSpecificOutput") or {}).get("hookEventName"), "PermissionRequest")
        self.assertEqual(decision.get("behavior"), "deny")
        self.assertIn("Blocked for safety", decision.get("message", ""))

    def test_run_hook_attempt_non_gate_worker_crash_stays_empty(self) -> None:
        """Non-gate events stay best-effort empty on crash (docs: empty = continue)."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {"hook_event_name": "SessionStart", "cwd": str(nested)}
            resolution = hook_state.resolve_hook_project(payload)

            result = hook_state.run_hook_attempt(
                resolution,
                "load_session",
                payload,
                lambda: (_ for _ in ()).throw(RuntimeError("no context")),
            )

        self.assertEqual(result, {})

    def test_run_hook_attempt_circuit_open_pretooluse_fails_closed(self) -> None:
        """Open circuit must not fail open on PreToolUse (empty would allow tool)."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            hook_state.record_hook_result(nested, "guard", "fail", reason="a")
            hook_state.record_hook_result(nested, "guard", "fail", reason="b")
            payload = {"hook_event_name": "PreToolUse", "cwd": str(nested)}
            resolution = hook_state.resolve_hook_project(payload)
            called = False

            def worker() -> dict:
                nonlocal called
                called = True
                return {}

            result = hook_state.run_hook_attempt(resolution, "guard", payload, worker)

        self.assertFalse(called)
        specific = result.get("hookSpecificOutput") or {}
        self.assertEqual(specific.get("permissionDecision"), "deny")
        self.assertIn("circuit open", specific.get("permissionDecisionReason", "").lower())

    def test_hook_receipt_redacts_prompt_and_records_output_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "repo"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            payload = {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "secret token ABC123",
                "cwd": str(nested),
            }

            resolution = hook_state.resolve_hook_project(payload)
            hook_state.run_hook_attempt(
                resolution,
                "guard",
                payload,
                lambda: {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": "Talk: caveman-strict.",
                    }
                },
            )
            receipt_path = (
                nested
                / ".codex"
                / "anyone-can-code"
                / "logs"
                / "hook-receipts.jsonl"
            )
            receipt_text = receipt_path.read_text(encoding="utf-8")
            receipt = json.loads(receipt_text.splitlines()[-1])

        self.assertNotIn("secret token", receipt_text)
        self.assertNotIn("ABC123", receipt_text)
        self.assertRegex(receipt["output_digest"], r"^[a-f0-9]{64}$")

    def test_load_session_script_returns_context_from_nested_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            nested = workspace / "zenfit-site"
            (nested / ".git").mkdir(parents=True)
            hook_state.ensure_project_layout(nested)
            (nested / "AGENTS.md").write_text("project rules\n", encoding="utf-8")
            payload = {
                "hook_event_name": "SessionStart",
                "source": "startup",
                "cwd": str(workspace),
            }

            result = subprocess.run(
                [
                    sys.executable,
                    str(PLUGIN_ROOT / "hooks" / "scripts" / "load_session.py"),
                ],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                timeout=10,
            )
            output = json.loads(result.stdout)
            receipt = json.loads(
                (
                    nested
                    / ".codex"
                    / "anyone-can-code"
                    / "logs"
                    / "hook-receipts.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hookSpecificOutput", output)
        self.assertIn("Project rules:", output["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(receipt["chosen_project"], str(nested.resolve()))
        self.assertEqual(receipt["final_effectiveness"], "useful")

    def test_action_receipt_blocks_risky_work_without_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with self.assertRaises(safety_receipts.SafetyGateError):
                safety_receipts.prepare_action(
                    target,
                    {
                        "name": "delete generated output",
                        "type": "delete",
                        "user_approval": "User approved cleanup",
                        "sandbox": "codex-native",
                    },
                    evidence=["cleanup target listed"],
                )
            receipts = list(
                (target / ".codex" / "anyone-can-code" / "artifacts" / "receipts").glob("*.md")
            )
            text = receipts[0].read_text(encoding="utf-8")

        self.assertEqual(len(receipts), 1)
        self.assertIn("Status: `blocked`", text)
        self.assertIn("backup or rollback path", text)

    def test_remote_action_requires_exact_authority_and_writes_readable_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            blocked = safety_receipts.write_action_receipt(
                target,
                {
                    "name": "push branch",
                    "type": "push",
                    "user_approval": "User said push this branch",
                    "sandbox": "codex-native",
                },
                status="blocked",
                evidence=["branch clean"],
            )
            approved = safety_receipts.prepare_action(
                target,
                {
                    "name": "push branch",
                    "type": "push",
                    "user_approval": "User said push this branch",
                    "remote_authority": "origin/main push explicitly requested",
                    "sandbox": "codex-native",
                },
                evidence=["branch clean"],
            )
            blocked_text = Path(blocked["receipt_markdown"]).read_text(encoding="utf-8")
            approved_text = Path(approved["receipt_markdown"]).read_text(encoding="utf-8")

        self.assertIn("remote authority evidence", blocked["missing"])
        self.assertIn("Status: `blocked`", blocked_text)
        self.assertIn("Status: `approved`", approved_text)
        self.assertIn("Remote: yes", approved_text)

    def test_canonical_state_renders_all_working_views_from_one_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            result = canonical_state.update_canonical_state(
                target,
                {
                    "active_goal": "Build login",
                    "active_task": "Add password reset",
                    "next_action": "Run interaction test",
                    "plan": ["Add reset form", "Send reset email"],
                    "tasks": [
                        {"name": "Add reset form", "state": "implemented"},
                        {"name": "Send reset email", "state": "in scope"},
                    ],
                    "verification": {
                        "level": "automated checks passed",
                        "evidence": ["12 tests passed"],
                        "stale": False,
                    },
                },
            )

            root = target / ".codex" / "anyone-can-code"
            workflow = json.loads((root / "state" / "workflow.json").read_text(encoding="utf-8"))
            status = (root / "state" / "state-current.md").read_text(encoding="utf-8")
            queue = (root / "state" / "task-queue.md").read_text(encoding="utf-8")
            resume = (root / "artifacts" / "resume-note.md").read_text(encoding="utf-8")
            guidance = (root / "artifacts" / "active-guidance.md").read_text(encoding="utf-8")
            snapshot = (root / "state" / "session-snapshot.md").read_text(encoding="utf-8")

        self.assertEqual(workflow["transaction_id"], result["transaction_id"])
        for rendered in (status, queue, resume, guidance, snapshot):
            self.assertIn(result["transaction_id"], rendered)
        self.assertIn("Add password reset", status)
        self.assertIn("Send reset email", queue)
        self.assertIn("Run interaction test", resume)

    def test_scope_change_preserves_history_and_invalidates_old_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            canonical_state.update_canonical_state(
                target,
                {
                    "active_goal": "Build login",
                    "active_task": "Password login",
                    "verification": {
                        "level": "real interaction verified",
                        "evidence": ["Login worked"],
                        "stale": False,
                    },
                },
            )

            changed = canonical_state.apply_scope_change(
                target,
                new_goal="Build passwordless login",
                new_task="Add email magic link",
                reason="User changed requirement",
            )

            history = (
                target
                / ".codex"
                / "anyone-can-code"
                / "state"
                / "state-history.jsonl"
            ).read_text(encoding="utf-8")

        self.assertEqual(changed["active_goal"], "Build passwordless login")
        self.assertEqual(changed["active_task"], "Add email magic link")
        self.assertTrue(changed["verification"]["stale"])
        self.assertEqual(changed["verification"]["level"], "unverified")
        self.assertIn("Password login", history)
        self.assertIn("superseded", history)

    def test_failed_derived_write_rolls_back_entire_state_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            before = canonical_state.update_canonical_state(
                target,
                {"active_goal": "Original", "active_task": "Original task"},
            )
            workflow_path = (
                target / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            )
            before_text = workflow_path.read_text(encoding="utf-8")

            with (
                mock.patch.object(
                    canonical_state,
                    "_write_text_atomic",
                    side_effect=OSError("disk full"),
                ),
                self.assertRaises(canonical_state.StateTransactionError),
            ):
                canonical_state.update_canonical_state(
                    target,
                    {"active_goal": "Changed", "active_task": "Changed task"},
                )

            after_text = workflow_path.read_text(encoding="utf-8")

        self.assertEqual(after_text, before_text)
        self.assertEqual(json.loads(after_text)["transaction_id"], before["transaction_id"])

    def test_active_task_capsule_keeps_recovery_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            result = canonical_state.update_canonical_state(
                target,
                {
                    "active_goal": "Build reliable resume",
                    "active_task": "Save active task capsule",
                    "decisions": ["Canonical state is truth"],
                    "boundaries": ["Do not guess missing context"],
                    "next_action": "Run recovery test",
                    "verification": {
                        "level": "automated checks passed",
                        "evidence": ["Capsule test passed"],
                        "stale": False,
                    },
                },
            )
            capsule_path = (
                target
                / ".codex"
                / "anyone-can-code"
                / "artifacts"
                / "active-task-capsule.md"
            )
            capsule_text = capsule_path.read_text(encoding="utf-8")

        capsule = result["active_task_capsule"]
        self.assertEqual(capsule["goal"], "Build reliable resume")
        self.assertEqual(capsule["decisions"], ["Canonical state is truth"])
        self.assertEqual(capsule["boundaries"], ["Do not guess missing context"])
        self.assertEqual(capsule["evidence"], ["Capsule test passed"])
        self.assertEqual(capsule["next_action"], "Run recovery test")
        self.assertIn(result["transaction_id"], capsule_text)

    def test_context_transition_saves_capsule_and_recovery_repairs_derived_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            canonical_state.update_canonical_state(
                target,
                {
                    "active_goal": "Build recovery",
                    "active_task": "Test restart",
                    "next_action": "Resume task",
                },
            )
            saved = canonical_state.prepare_context_transition(
                target,
                transition="compaction",
            )
            status_path = (
                target
                / ".codex"
                / "anyone-can-code"
                / "state"
                / "state-current.md"
            )
            status_path.write_text("stale transaction\n", encoding="utf-8")

            uncertain = canonical_state.recover_from_canonical_state(target)
            repaired = canonical_state.recover_from_canonical_state(target, repair=True)
            status_text = status_path.read_text(encoding="utf-8")

        self.assertEqual(saved["recovery"]["last_transition"], "compaction")
        self.assertEqual(uncertain["status"], "uncertain")
        self.assertIn("state-current.md transaction mismatch", uncertain["uncertainty"])
        self.assertTrue(repaired["repaired"])
        self.assertEqual(repaired["status"], "ready")
        self.assertIn(repaired["transaction_id"], status_text)

    def test_recover_from_compaction_reanchors_and_repairs_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            canonical_state.update_canonical_state(
                target,
                {
                    "active_goal": "Build compaction recovery",
                    "active_task": "Re-anchor session",
                    "next_action": "Continue from capsule",
                },
            )
            status_path = (
                target
                / ".codex"
                / "anyone-can-code"
                / "state"
                / "state-current.md"
            )
            status_path.write_text("stale transaction\n", encoding="utf-8")

            recovery = canonical_state.recover_from_compaction(target)

        self.assertEqual(recovery["status"], "ready")
        self.assertTrue(recovery["repaired"])
        self.assertEqual(recovery["transition"], "compaction")
        self.assertEqual(recovery["capsule"]["task"], "Re-anchor session")
        self.assertEqual(recovery["next_action"], "Continue from capsule")

    def test_recovery_reports_missing_context_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            canonical_state.update_canonical_state(
                target,
                {"active_goal": "Build recovery"},
            )

            recovery = canonical_state.recover_from_canonical_state(target)

        self.assertEqual(recovery["status"], "uncertain")
        self.assertIn("active task missing", recovery["uncertainty"])
        self.assertIn("next action missing", recovery["uncertainty"])

    def test_acc_hook_disable_marker_applies_to_descendants_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marked_tree = root / "plugin-development"
            nested_repo = marked_tree / "inspiration" / "sample"
            outside_repo = root / "other-project"
            marker = marked_tree / ".codex" / "anyone-can-code-hooks.disabled"
            marker.parent.mkdir(parents=True)
            marker.write_text(
                "ACC hooks disabled for this directory tree.\n",
                encoding="utf-8",
            )
            nested_repo.mkdir(parents=True)
            outside_repo.mkdir()

            self.assertTrue(hook_state.acc_hooks_disabled(nested_repo))
            self.assertFalse(hook_state.acc_hooks_disabled(outside_repo))

    def test_all_acc_hooks_noop_without_state_writes_below_marker(self) -> None:
        payloads = {
            "guard.py": {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "build a website",
            },
            "audit.py": {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "echo hi"},
                "tool_response": {"exit_code": 0},
            },
            "load_session.py": {
                "hook_event_name": "SessionStart",
                "source": "startup",
            },
            "save_session.py": {
                "hook_event_name": "Stop",
                "turn_id": "test-turn",
                "stop_hook_active": False,
                "last_assistant_message": "test",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "plugin-development"
            repo = tree / "sample-project"
            marker = tree / ".codex" / "anyone-can-code-hooks.disabled"
            marker.parent.mkdir(parents=True)
            marker.write_text("disabled\n", encoding="utf-8")
            repo.mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            for script_name, payload in payloads.items():
                with self.subTest(script=script_name):
                    result = subprocess.run(
                        [sys.executable, str(PLUGIN_ROOT / "hooks" / "scripts" / script_name)],
                        input=json.dumps(payload),
                        text=True,
                        capture_output=True,
                        cwd=repo,
                        timeout=20,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout), {})
                    self.assertFalse((repo / ".codex" / "anyone-can-code").exists())

    def test_acc_repo_does_not_disable_all_codex_hooks(self) -> None:
        repo_root = PLUGIN_ROOT.parents[1]
        configs = [PLUGIN_ROOT / "reference" / "project" / ".codex" / "config.toml"]
        local_config = repo_root / ".codex" / "config.toml"
        if local_config.exists():
            configs.append(local_config)

        for config_path in configs:
            with self.subTest(config=config_path):
                config = config_path.read_text(encoding="utf-8")
                self.assertNotIn("hooks = false", config)
                self.assertNotIn("plugin_hooks = false", config)

    def test_setup_uses_selected_memory_path_and_writes_plain_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            selected = target / "my-readable-memory" / "notes"
            receipt = setup.bootstrap_project(target, memory_path=selected, viewer_mode="none")
            preferences = json.loads(
                (target / ".codex" / "anyone-can-code" / "settings" / "preferences.json").read_text(
                    encoding="utf-8"
                )
            )
            receipt_exists = Path(receipt["receipt_markdown"]).exists()

        self.assertEqual(preferences["memory_path"], str(selected))
        self.assertEqual(preferences["viewer_mode"], "none")
        self.assertTrue(receipt_exists)
        self.assertEqual(receipt["viewer"]["action"], "none")
        self.assertEqual(receipt["imports"]["status"], "not requested")

    def test_setup_previews_imports_without_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = target / "session.md"
            source.write_text("User selected session", encoding="utf-8")
            receipt = setup.bootstrap_project(
                target,
                import_sources=[source],
                import_scope="project",
                confirm_import=False,
            )

        self.assertEqual(receipt["imports"]["status"], "preview only")
        self.assertEqual(receipt["imports"]["scope"], "project")
        self.assertEqual(receipt["imports"]["selected_paths"], [str(source.resolve())])
        self.assertEqual(receipt["imports"]["imported"], 0)

    def test_setup_import_requires_confirmation_and_keeps_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = target / "session.md"
            source.write_text("Use receipts for setup changes", encoding="utf-8")
            receipt = setup.bootstrap_project(
                target,
                import_sources=[source],
                import_scope="project",
                confirm_import=True,
            )
            source_still_exists = source.exists()

        self.assertEqual(receipt["imports"]["status"], "completed")
        self.assertEqual(receipt["imports"]["imported"], 1)
        self.assertTrue(source_still_exists)

    def test_setup_reports_import_rollback_without_hiding_failure(self) -> None:
        fake_server = mock.Mock()
        fake_server.import_session_files.return_value = {
            "status": "rolled_back",
            "imported_count": 0,
            "rollback_receipt_path": "rollback.json",
        }
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = target / "session.md"
            source.write_text("Selected session", encoding="utf-8")
            with mock.patch.object(setup, "load_memory_server", return_value=fake_server):
                receipt = setup.bootstrap_project(
                    target,
                    import_sources=[source],
                    import_scope="project",
                    confirm_import=True,
                )

        self.assertEqual(receipt["imports"]["status"], "rolled back")
        self.assertEqual(receipt["imports"]["imported"], 0)
        self.assertEqual(receipt["imports"]["receipt_path"], "rollback.json")

    def test_obsidian_absent_never_blocks_no_viewer_setup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(setup, "detect_obsidian", return_value=None):
                receipt = setup.bootstrap_project(Path(tmp), viewer_mode="none")

        self.assertFalse(receipt["viewer"]["detected"])
        self.assertEqual(receipt["viewer"]["status"], "not requested")

    def test_obsidian_present_can_be_selected_without_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_obsidian = Path(tmp) / "Obsidian.exe"
            with mock.patch.object(setup, "detect_obsidian", return_value=fake_obsidian):
                receipt = setup.bootstrap_project(Path(tmp), viewer_mode="obsidian")

        self.assertTrue(receipt["viewer"]["detected"])
        self.assertEqual(receipt["viewer"]["action"], "none")
        self.assertEqual(receipt["viewer"]["status"], "not requested")

    def test_obsidian_action_requires_explicit_consent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with self.assertRaises(ValueError):
                setup.bootstrap_project(
                    target,
                    viewer_mode="obsidian",
                    viewer_action="download-page",
                    consent_viewer_action=False,
                )
            setup_root_exists = (target / ".codex" / "anyone-can-code").exists()

        self.assertFalse(setup_root_exists)

    def test_obsidian_install_uses_winget_without_acceptance_flags(self) -> None:
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with tempfile.TemporaryDirectory() as tmp:
            with (
                mock.patch.object(setup, "detect_obsidian", return_value=None),
                mock.patch.object(setup.shutil, "which", return_value="winget.exe"),
                mock.patch.object(setup.subprocess, "run", return_value=completed) as run,
            ):
                receipt = setup.bootstrap_project(
                    Path(tmp),
                    viewer_mode="obsidian",
                    viewer_action="install",
                    consent_viewer_action=True,
                )

        command = run.call_args.args[0]
        self.assertEqual(
            command,
            ["winget.exe", "install", "--id", "Obsidian.Obsidian", "--exact", "--source", "winget"],
        )
        self.assertNotIn("--accept-package-agreements", command)
        self.assertNotIn("--accept-source-agreements", command)
        self.assertEqual(receipt["viewer"]["status"], "install command completed")

    def test_failed_obsidian_install_does_not_block_setup(self) -> None:
        completed = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="failed")
        with tempfile.TemporaryDirectory() as tmp:
            with (
                mock.patch.object(setup, "detect_obsidian", return_value=None),
                mock.patch.object(setup.shutil, "which", return_value="winget.exe"),
                mock.patch.object(setup.subprocess, "run", return_value=completed),
            ):
                receipt = setup.bootstrap_project(
                    Path(tmp),
                    viewer_mode="obsidian",
                    viewer_action="install",
                    consent_viewer_action=True,
                )
                receipt_exists = Path(receipt["receipt_markdown"]).exists()

        self.assertEqual(receipt["viewer"]["status"], "install command failed")
        self.assertEqual(receipt["viewer"]["exit_code"], 1)
        self.assertTrue(receipt_exists)

    def test_official_download_page_does_not_run_installer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with (
                mock.patch.object(setup, "detect_obsidian", return_value=None),
                mock.patch.object(setup.webbrowser, "open", return_value=True) as opened,
                mock.patch.object(setup.subprocess, "run") as run,
            ):
                receipt = setup.bootstrap_project(
                    Path(tmp),
                    viewer_mode="obsidian",
                    viewer_action="download-page",
                    consent_viewer_action=True,
                )

        opened.assert_called_once_with(setup.OBSIDIAN_DOWNLOAD_URL)
        run.assert_not_called()
        self.assertEqual(receipt["viewer"]["status"], "official download page opened")
        self.assertEqual(receipt["viewer"]["instructions"], setup.OBSIDIAN_DOWNLOAD_URL)

    def test_manual_vault_open_instructions_name_exact_memory_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            selected = target / "founder-memory" / "notes"
            with mock.patch.object(setup.webbrowser, "open", return_value=False):
                receipt = setup.bootstrap_project(
                    target,
                    memory_path=selected,
                    viewer_mode="obsidian",
                    viewer_action="open-vault",
                    consent_viewer_action=True,
                )

        instructions = receipt["viewer"]["instructions"]
        self.assertIn('choose "Open folder as vault"', instructions)
        self.assertIn(str(selected), instructions)
        self.assertEqual(receipt["viewer"]["status"], "automatic vault open unavailable")

    def test_existing_memory_file_conflict_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            selected = target / "memory-conflict"
            selected.write_text("keep me", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                setup.bootstrap_project(target, memory_path=selected)

            self.assertEqual(selected.read_text(encoding="utf-8"), "keep me")

    def test_setup_writes_builder_persona_and_workflow_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            setup.bootstrap_project(target)

            preferences = json.loads(
                (target / ".codex" / "anyone-can-code" / "settings" / "preferences.json").read_text(
                    encoding="utf-8"
                )
            )
            workflow = json.loads(
                (target / ".codex" / "anyone-can-code" / "state" / "workflow.json").read_text(
                    encoding="utf-8"
                )
            )
            status_text = (
                target / ".codex" / "anyone-can-code" / "state" / "state-current.md"
            ).read_text(encoding="utf-8")
            resume_text = (
                target / ".codex" / "anyone-can-code" / "artifacts" / "resume-note.md"
            ).read_text(encoding="utf-8")
            memory_notes_exists = (target / ".codex" / "anyone-can-code" / "memory" / "notes").exists()
            memory_index_exists = (target / ".codex" / "anyone-can-code" / "memory" / "index").exists()
            memory_imports_exists = (target / ".codex" / "anyone-can-code" / "memory" / "imports").exists()

        self.assertEqual(preferences["persona_mode"], "builder")
        self.assertEqual(preferences["persona_allowed_modes"], ["builder", "developer", "mixed"])
        self.assertEqual(preferences["communication_mode"], "caveman-strict")
        self.assertEqual(preferences["repo_mode"], "unknown")
        self.assertEqual(preferences["memory_mode"], "portable-markdown")
        self.assertEqual(preferences["memory_path"], ".codex/anyone-can-code/memory/notes")
        self.assertEqual(preferences["viewer_mode"], "none")
        self.assertEqual(preferences["import_sources"], [])
        self.assertEqual(preferences["import_scope"], "ask")
        self.assertTrue(preferences["production_repo_caution"])
        self.assertEqual(preferences["git_mode"], "auto")
        self.assertEqual(workflow["persona_mode"], "builder")
        self.assertEqual(workflow["repo_mode"], "unknown")
        self.assertEqual(workflow["setup_state"], "ready")
        self.assertEqual(workflow["memory_mode"], "portable-markdown")
        self.assertEqual(workflow["viewer_mode"], "none")
        self.assertNotIn("status_line", workflow)
        self.assertNotIn("work_state", workflow)
        self.assertNotIn("verification_state", workflow)
        self.assertNotIn("states", workflow)
        self.assertNotIn("unverified", workflow)
        self.assertEqual(workflow["failures"], [])
        self.assertEqual(workflow["workflow_owner"], "acc")
        self.assertEqual(workflow["verification"]["level"], "unverified")
        self.assertTrue(workflow["transaction_id"])
        self.assertIn(workflow["transaction_id"], status_text)
        self.assertIn(workflow["transaction_id"], resume_text)
        self.assertTrue(memory_notes_exists)
        self.assertTrue(memory_index_exists)
        self.assertTrue(memory_imports_exists)

    def test_doctor_reports_persona_and_workflow_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            setup.bootstrap_project(target)

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                report = doctor.Doctor(json_mode=True).run_all()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in report["results"]}
        self.assertEqual(by_check["project_layout"]["status"], "PASS")
        self.assertEqual(by_check["persona_settings"]["status"], "PASS")
        self.assertEqual(by_check["workflow_state"]["status"], "PASS")
        self.assertEqual(by_check["workflow_observability"]["status"], "PASS")
        self.assertEqual(by_check["legacy_state_fields"]["status"], "PASS")
        self.assertEqual(by_check["repo_mode"]["status"], "PASS")
        self.assertEqual(by_check["memory_storage"]["status"], "PASS")
        self.assertEqual(by_check["memory_viewer"]["status"], "PASS")
        self.assertEqual(by_check["state_agreement"]["status"], "PASS")

    def test_doctor_warns_when_settings_and_workflow_disagree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            setup.bootstrap_project(target)
            workflow_path = target / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["viewer_mode"] = "obsidian"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                instance = doctor.Doctor(json_mode=True)
                instance.run_project_state()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in instance.results}
        self.assertEqual(by_check["state_agreement"]["status"], "WARN")
        self.assertIn("Next:", by_check["state_agreement"]["evidence"])

    def test_canonical_state_strips_legacy_truth_fields_from_old_session_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            workflow_path = target / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            workflow_path.parent.mkdir(parents=True)
            workflow_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "workflow_owner": "acc",
                        "active_goal": "Refine Zenfit",
                        "active_task": "Repair truth",
                        "verification": {
                            "level": "unverified",
                            "evidence": [],
                            "stale": True,
                        },
                        "states": {
                            "build": "verified",
                            "tests": "verified",
                            "deploy": "deferred",
                        },
                        "status_line": "Status: build verified, tests verified, deploy deferred",
                        "work_state": "verified",
                        "verification_state": "verified",
                        "evidence": ["old stale proof"],
                        "unverified": [],
                        "silent_failures": [],
                        "uncertainty": [],
                    }
                ),
                encoding="utf-8",
            )

            read_state = canonical_state.read_canonical_state(target)
            rewritten = canonical_state.update_canonical_state(
                target,
                {"next_action": "Continue from canonical state"},
            )
            saved = json.loads(workflow_path.read_text(encoding="utf-8"))

        for field in canonical_state.LEGACY_TRUTH_FIELDS:
            self.assertNotIn(field, read_state)
            self.assertNotIn(field, rewritten)
            self.assertNotIn(field, saved)
        self.assertEqual(saved["verification"]["level"], "unverified")
        self.assertTrue(saved["verification"]["stale"])
        self.assertEqual(saved["verification"]["evidence"], [])

    def test_doctor_warns_when_raw_workflow_still_has_legacy_truth_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            setup.bootstrap_project(target)
            workflow_path = target / ".codex" / "anyone-can-code" / "state" / "workflow.json"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["status_line"] = "Status: build verified, tests verified"
            workflow["verification_state"] = "verified"
            workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                instance = doctor.Doctor(json_mode=True)
                instance.run_project_state()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in instance.results}
        self.assertEqual(by_check["legacy_state_fields"]["status"], "WARN")
        self.assertIn("status_line", by_check["legacy_state_fields"]["evidence"])
        self.assertIn("verification_state", by_check["legacy_state_fields"]["evidence"])

    def test_doctor_keeps_storage_healthy_when_selected_viewer_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with mock.patch.object(setup, "detect_obsidian", return_value=None):
                setup.bootstrap_project(target, viewer_mode="obsidian")

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                with mock.patch.object(doctor.shutil, "which", return_value=None):
                    report = doctor.Doctor(json_mode=True).run_all()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in report["results"]}
        self.assertEqual(by_check["memory_storage"]["status"], "PASS")
        self.assertEqual(by_check["memory_viewer"]["status"], "WARN")
        self.assertIn("Markdown storage still works", by_check["memory_viewer"]["evidence"])

    def test_doctor_accepts_acc_only_ancestor_marker_without_disabling_other_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "plugin-development"
            target = tree / "sample-project"
            marker = tree / ".codex" / "anyone-can-code-hooks.disabled"
            marker.parent.mkdir(parents=True)
            marker.write_text("disabled\n", encoding="utf-8")
            (target / ".codex").mkdir(parents=True)
            (target / ".codex" / "config.toml").write_text(
                "[features]\nmemories = false\n",
                encoding="utf-8",
            )

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                instance = doctor.Doctor(json_mode=True)
                instance.run_project_config()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        result = instance.results[0]
        self.assertEqual(result["check"], "project_hooks_mode")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("ACC-only marker", result["evidence"])

    def test_doctor_reports_optional_hook_health_recovery_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                instance = doctor.Doctor(json_mode=True)
                instance.run_hook_health()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        result = instance.results[0]
        self.assertEqual(result["check"], "hook_health")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("Next:", result["evidence"])

    def test_doctor_summarizes_latest_hook_receipt_effectiveness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".git").mkdir()
            hook_state.ensure_project_layout(target)
            payload = {"hook_event_name": "SessionStart", "cwd": str(target)}
            resolution = hook_state.resolve_hook_project(payload)
            hook_state.run_hook_attempt(
                resolution,
                "load_session",
                payload,
                lambda: {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "Talk: caveman-strict.",
                    }
                },
            )

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                instance = doctor.Doctor(json_mode=True)
                instance.run_hook_health()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        result = instance.results[0]
        self.assertEqual(result["check"], "hook_health")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("latest receipts", result["evidence"])
        self.assertIn("useful", result["evidence"])

    def test_doctor_blocks_silent_repair_of_incomplete_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            runtime = target / "cache" / "anyone-can-code"
            (runtime / ".codex-plugin").mkdir(parents=True)
            (runtime / ".codex-plugin" / "plugin.json").write_text(
                json.dumps({"name": "anyone-can-code", "version": "1.0.0"}),
                encoding="utf-8",
            )
            info = {
                "plugin_source_root": str(runtime),
                "installed_plugin_root": str(runtime),
                "plugin_source_version": "1.0.0",
                "installed_runtime_version": "1.0.0",
                "project_state_version": "1.0.0",
                "marketplace_root": str(target),
                "marketplace_name": "acc",
                "managed_marketplace_configured": True,
                "marketplace_upgrade_mode": "local",
                "managed_marketplace_source": str(target),
                "wrong_root_hint": None,
            }

            old_project_root = doctor.PROJECT_ROOT
            doctor.PROJECT_ROOT = target
            try:
                with mock.patch.object(doctor.runtime_info, "build_runtime_info", return_value=info):
                    instance = doctor.Doctor(json_mode=True)
                    instance.run_runtime_truth()
            finally:
                doctor.PROJECT_ROOT = old_project_root

        by_check = {item["check"]: item for item in instance.results}
        self.assertEqual(by_check["installed_source"]["status"], "WARN")
        self.assertIn("do not edit another plugin", by_check["installed_source"]["evidence"])

    def test_doctor_conflict_control_names_owner_and_fallback(self) -> None:
        plugins = [
            {
                "name": "flow-next",
                "capability_text": "workflow orchestrator project state",
                "manifest": "flow/plugin.json",
            }
        ]

        with mock.patch.object(doctor.front_door, "scan_installed_plugins", return_value=plugins):
            instance = doctor.Doctor(json_mode=True)
            instance.run_plugin_conflicts()

        result = instance.results[0]
        self.assertEqual(result["check"], "plugin_conflicts")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("ACC keeps workflow ownership and fallback", result["evidence"])

    def test_doctor_warns_on_duplicate_acc_runtime(self) -> None:
        plugins = [
            {"name": "anyone-can-code", "capability_text": "acc", "manifest": "one/plugin.json"},
            {"name": "anyone-can-code", "capability_text": "acc", "manifest": "two/plugin.json"},
        ]

        with mock.patch.object(doctor.front_door, "scan_installed_plugins", return_value=plugins):
            instance = doctor.Doctor(json_mode=True)
            instance.run_plugin_conflicts()

        result = instance.results[0]
        self.assertEqual(result["check"], "plugin_conflicts")
        self.assertEqual(result["status"], "WARN")
        self.assertIn("do not edit other plugins", result["evidence"])

    def test_runtime_version_comparison_ignores_codex_cachebuster_metadata(self) -> None:
        self.assertEqual(
            doctor.runtime_info.compare_versions(
                "1.0.0",
                "1.0.0+codex.20260613140139",
            ),
            0,
        )
        self.assertLess(doctor.runtime_info.compare_versions("1.0.0", "1.0.1+codex.local"), 0)

    def test_update_migrates_only_project_owned_legacy_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            legacy = target / ".codex" / "anyone-can-code" / "learning" / "feedback.jsonl"
            legacy.parent.mkdir(parents=True)
            legacy.write_text(json.dumps({"summary": "Old project lesson"}) + "\n", encoding="utf-8")
            unrelated = target / "user-session.jsonl"
            unrelated.write_text(json.dumps({"summary": "Do not scan me"}) + "\n", encoding="utf-8")

            receipt = update.migrate_legacy_memory(target)

        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["imported_count"], 1)
        self.assertEqual(receipt["sources"], [str(legacy)])
        self.assertNotIn(str(unrelated), receipt["sources"])

    def test_update_stops_before_setup_when_memory_migration_rolls_back(self) -> None:
        before = {
            "plugin_version": "0.9.0",
            "hook_mode": "bundled",
            "memory_path": ".codex/anyone-can-code/memory/notes",
            "viewer_mode": "none",
        }
        runtime = {
            "plugin_source_version": "1.0.0",
            "installed_runtime_version": "1.0.0",
            "project_root": "C:/project",
            "next_action": "migrate-project",
        }
        rollback = {
            "status": "rolled_back",
            "rollback_receipt_path": "rollback.json",
        }
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with (
                mock.patch.object(update, "load_install_state", return_value=before),
                mock.patch.object(update.runtime_info, "build_runtime_info", return_value=runtime),
                mock.patch.object(update, "backup_dir", return_value=target / "backup"),
                mock.patch.object(update, "backup_supported_data"),
                mock.patch.object(update, "quarantine_corrupt_files", return_value=[]),
                mock.patch.object(update, "migrate_legacy_memory", return_value=rollback),
                mock.patch.object(update, "run_setup") as run_setup,
                mock.patch.object(update, "write_migration_journal") as write_journal,
            ):
                update.migrate(target)

        run_setup.assert_not_called()
        write_journal.assert_not_called()

    def test_setup_repairs_missing_persona_fields_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            settings_dir = target / ".codex" / "anyone-can-code" / "settings"
            state_dir = target / ".codex" / "anyone-can-code" / "state"
            settings_dir.mkdir(parents=True)
            state_dir.mkdir(parents=True)
            (settings_dir / "preferences.json").write_text(
                json.dumps({"schema_version": 2, "communication_mode": "caveman-strict"}),
                encoding="utf-8",
            )
            (state_dir / "workflow.json").write_text(
                json.dumps({"schema_version": 2, "phase": "idle"}),
                encoding="utf-8",
            )

            setup.bootstrap_project(target)

            preferences = json.loads((settings_dir / "preferences.json").read_text(encoding="utf-8"))
            workflow = json.loads((state_dir / "workflow.json").read_text(encoding="utf-8"))

        self.assertEqual(preferences["persona_mode"], "builder")
        self.assertEqual(preferences["repo_mode"], "unknown")
        self.assertEqual(workflow["persona_mode"], "builder")
        self.assertEqual(workflow["repo_mode"], "unknown")
        self.assertEqual(workflow["setup_state"], "ready")

    def test_save_session_does_not_overwrite_project_agents_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_path = target / "AGENTS.md"
            agents_path.write_text("project rules stay\n", encoding="utf-8")

            save_session.write_session_snapshot(
                target,
                "session summary",
                {
                    "phase": "idle",
                    "route": "status",
                    "last_task": "check",
                    "next_step": "next",
                    "memory_mode": "portable-markdown",
                },
            )

            snapshot_path = target / ".codex" / "anyone-can-code" / "state" / "session-snapshot.md"
            self.assertEqual(agents_path.read_text(encoding="utf-8"), "project rules stay\n")
            self.assertTrue(snapshot_path.exists())

    def test_hooks_use_plugin_root_command_and_windows_override(self) -> None:
        """One package: Codex PLUGIN_ROOT command + commandWindows (docs shape)."""
        hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        for event, groups in hooks["hooks"].items():
            for group in groups:
                for hook in group.get("hooks") or []:
                    if hook.get("type", "command") != "command":
                        continue
                    cmd = str(hook.get("command") or "")
                    win = str(hook.get("commandWindows") or "")
                    with self.subTest(event=event):
                        self.assertIn("PLUGIN_ROOT", cmd)
                        self.assertIn("python3", cmd)
                        self.assertIn("PLUGIN_ROOT", win)
                        self.assertTrue(win.startswith("py -3") or "py -3" in win)

    @unittest.skipUnless(os.name == "nt", "Windows hook shell regression")
    def test_hook_commands_run_from_parent_workspace_without_plugin_env_under_cmd(self) -> None:
        hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        repo_root = PLUGIN_ROOT.parents[2]
        workspace_root = repo_root.parent
        env = os.environ.copy()
        env.pop("PLUGIN_ROOT", None)
        env.pop("CLAUDE_PLUGIN_ROOT", None)

        cases = [
            (
                self._windows_hook_command(hooks["hooks"]["PreToolUse"][0]["hooks"][0]),
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "cwd": str(workspace_root),
                },
            ),
            (
                self._windows_hook_command(hooks["hooks"]["PostToolUse"][0]["hooks"][0]),
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "tool_response": {"exit_code": 0},
                    "cwd": str(workspace_root),
                },
            ),
            (
                self._windows_hook_command(hooks["hooks"]["Stop"][0]["hooks"][0]),
                {
                    "hook_event_name": "Stop",
                    "turn_id": "test-turn",
                    "stop_hook_active": False,
                    "last_assistant_message": "test",
                    "cwd": str(workspace_root),
                },
            ),
        ]

        for command, payload in cases:
            with self.subTest(event=payload["hook_event_name"]):
                result = subprocess.run(
                    ["cmd.exe", "/c", command],
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    cwd=workspace_root,
                    env=env,
                    timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows hook shell regression")
    def test_hook_commands_accept_marketplace_repo_as_plugin_root(self) -> None:
        hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        marketplace_repo = PLUGIN_ROOT.parents[1]
        workspace_root = marketplace_repo.parent
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(marketplace_repo)
        env.pop("CLAUDE_PLUGIN_ROOT", None)

        cases = [
            (
                self._windows_hook_command(
                    hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]
                ),
                {
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "test",
                    "cwd": str(workspace_root),
                },
            ),
            (
                self._windows_hook_command(hooks["hooks"]["PreToolUse"][0]["hooks"][0]),
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "cwd": str(workspace_root),
                },
            ),
            (
                self._windows_hook_command(hooks["hooks"]["PostToolUse"][0]["hooks"][0]),
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "tool_response": {"exit_code": 0},
                    "cwd": str(workspace_root),
                },
            ),
        ]

        for command, payload in cases:
            with self.subTest(event=payload["hook_event_name"]):
                result = subprocess.run(
                    command,
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    cwd=workspace_root,
                    env=env,
                    shell=True,
                    timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "{}")


if __name__ == "__main__":
    unittest.main()
