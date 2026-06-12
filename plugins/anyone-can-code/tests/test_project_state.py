from __future__ import annotations

import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

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
save_session = load_hook_script("save_session")


class ProjectStateTests(unittest.TestCase):
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

        self.assertEqual(preferences["persona_mode"], "builder")
        self.assertEqual(preferences["persona_allowed_modes"], ["builder", "developer", "mixed"])
        self.assertEqual(preferences["communication_mode"], "caveman-strict")
        self.assertEqual(preferences["repo_mode"], "unknown")
        self.assertEqual(workflow["persona_mode"], "builder")
        self.assertEqual(workflow["repo_mode"], "unknown")
        self.assertEqual(workflow["setup_state"], "ready")

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
        self.assertEqual(by_check["repo_mode"]["status"], "PASS")

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
                    "memory_mode": "mcp-first",
                },
            )

            snapshot_path = target / ".codex" / "anyone-can-code" / "state" / "session-snapshot.md"
            self.assertEqual(agents_path.read_text(encoding="utf-8"), "project rules stay\n")
            self.assertTrue(snapshot_path.exists())


if __name__ == "__main__":
    unittest.main()
