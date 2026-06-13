from __future__ import annotations

import json
import importlib.util
import os
import subprocess
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


class ProjectStateTests(unittest.TestCase):
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
        self.assertEqual(workflow["persona_mode"], "builder")
        self.assertEqual(workflow["repo_mode"], "unknown")
        self.assertEqual(workflow["setup_state"], "ready")
        self.assertEqual(workflow["memory_mode"], "portable-markdown")
        self.assertEqual(workflow["viewer_mode"], "none")
        self.assertEqual(
            workflow["status_line"],
            "Status: build in scope, tests in scope, deploy deferred",
        )
        self.assertEqual(workflow["unverified"], ["build", "tests"])
        self.assertEqual(workflow["failures"], [])
        self.assertEqual(workflow["silent_failures"], [])
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
        self.assertEqual(by_check["repo_mode"]["status"], "PASS")
        self.assertEqual(by_check["memory_storage"]["status"], "PASS")
        self.assertEqual(by_check["memory_viewer"]["status"], "PASS")

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
                hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"],
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "cwd": str(workspace_root),
                },
            ),
            (
                hooks["hooks"]["PostToolUse"][0]["hooks"][0]["command"],
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"},
                    "tool_response": {"exit_code": 0},
                    "cwd": str(workspace_root),
                },
            ),
            (
                hooks["hooks"]["Stop"][0]["hooks"][0]["command"],
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


if __name__ == "__main__":
    unittest.main()
