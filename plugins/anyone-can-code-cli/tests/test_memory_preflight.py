from __future__ import annotations

import importlib.util
import json
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


memory_preflight = load_script("memory_preflight")
setup = load_script("setup")
doctor = load_script("doctor")


class MemoryPreflightTests(unittest.TestCase):
    def test_learned_mistake_is_recalled_after_setup_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            setup.bootstrap_project(project_root)
            stored = memory_preflight.store_learned_memory(
                project_root,
                "After plugin update, recall prior skill-selection mistakes before routing specialists.",
                evidence="user correction from prior session",
            )

            setup.bootstrap_project(project_root, force=True)
            recalled = memory_preflight.retrieve_relevant_memory(
                project_root,
                "Use plugin after update and choose skills without repeating mistakes",
            )

        self.assertTrue(stored["stored"])
        self.assertTrue(recalled["used"])
        self.assertEqual(recalled["count"], 1)
        self.assertIn("Relevant memory used: 1 item", recalled["visible_line"])
        self.assertIn("route-specialist", recalled["required_before"])
        self.assertIn("skill-selection mistakes", recalled["items"][0]["summary"])

    def test_memory_preflight_uses_configured_memory_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            selected_notes = project_root / "human-readable-memory" / "notes"
            setup.bootstrap_project(project_root, memory_path=selected_notes)

            stored = memory_preflight.store_learned_memory(
                project_root,
                "User wants a full request analysis before choosing exact skills.",
            )
            recalled = memory_preflight.retrieve_relevant_memory(
                project_root,
                "full analysis before skills",
            )
            stored_path = Path(str(stored["path"]))
            stored_path_exists = stored_path.is_file()
            stored_path_relative = stored_path.resolve().relative_to(selected_notes.parent.resolve())

        self.assertTrue(stored["path"])
        self.assertTrue(stored_path_exists)
        self.assertEqual(stored_path_relative.parts[0], "notes")
        self.assertTrue(recalled["used"])

    def test_doctor_reports_memory_preflight(self) -> None:
        instance = doctor.Doctor(json_mode=True)
        instance.run_memory_preflight()

        result = instance.results[0]
        self.assertEqual(result["check"], "memory_preflight")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("recalled before first action", result["evidence"])

    def test_cli_outputs_visible_memory_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            setup.bootstrap_project(project_root)
            memory_preflight.store_learned_memory(
                project_root,
                "Use remembered mistake when routing plugin skills.",
            )

            payload = memory_preflight.retrieve_relevant_memory(
                project_root,
                "routing plugin skills remembered mistake",
            )

        serialized = json.dumps(payload)
        self.assertIn("Relevant memory used:", serialized)
        self.assertIn("portable-markdown", serialized)


if __name__ == "__main__":
    unittest.main()
