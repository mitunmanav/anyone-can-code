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


front_door = load_script("front_door")


class FrontDoorTests(unittest.TestCase):
    def test_classifies_supported_starting_points(self) -> None:
        cases = {
            "I want to build a website": "idea",
            "Use the requirements in SPEC.md": "written-spec",
            "Work in this existing repo": "existing-repo",
            "Add password reset to this app": "feature-request",
            "Fix the login crash": "bug-fix",
            "Polish this page and review the UX": "polish-review",
            "Ship this release": "ship-verify",
            "Verify what changed": "ship-verify",
        }

        for request, expected in cases.items():
            with self.subTest(request=request):
                self.assertEqual(front_door.classify_entry_mode(request), expected)

    def test_vague_idea_reuses_product_intake_route(self) -> None:
        result = front_door.route_request("I want to build a website", plugins=[])

        self.assertEqual(result["entry_mode"], "idea")
        self.assertEqual(result["product_type"], "website")
        self.assertEqual(result["banner"], "Detected: idea + website")
        self.assertEqual(result["route"], ["intake", "checklist", "plan"])
        self.assertLessEqual(len(result["intake"]["questions"]), 5)

    def test_existing_repo_feature_uses_combined_banner(self) -> None:
        result = front_door.route_request(
            "Add password reset to this existing repo",
            plugins=[],
        )

        self.assertEqual(result["entry_mode"], "feature-request")
        self.assertEqual(result["banner"], "Detected: existing repo + feature request")
        self.assertEqual(result["route"], ["plan", "execute", "verify"])

    def test_requirement_change_updates_plan_then_resumes(self) -> None:
        result = front_door.route_request(
            "Actually add team accounts instead",
            {"workflow_active": True, "resume_step": "execute"},
        )

        self.assertEqual(result["entry_mode"], "requirement-change")
        self.assertEqual(result["route"], ["update-plan", "update-state", "execute"])

    def test_manifest_scan_skips_malformed_and_reads_skill_descriptions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Path(temp_dir)
            plugin_root = cache / "market" / "browser-tools" / "1.0.0"
            (plugin_root / ".codex-plugin").mkdir(parents=True)
            (plugin_root / "skills" / "browser").mkdir(parents=True)
            (plugin_root / ".codex-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "browser-tools",
                        "description": "Open and test local websites.",
                        "skills": "./skills/",
                    }
                ),
                encoding="utf-8",
            )
            (plugin_root / "skills" / "browser" / "SKILL.md").write_text(
                "---\nname: browser\ndescription: Navigate localhost and take screenshots.\n---\n",
                encoding="utf-8",
            )
            bad_root = cache / "market" / "broken" / "1.0.0" / ".codex-plugin"
            bad_root.mkdir(parents=True)
            (bad_root / "plugin.json").write_text("{bad json", encoding="utf-8")

            plugins = front_door.scan_installed_plugins(cache)

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "browser-tools")
        self.assertIn("navigate localhost", plugins[0]["capability_text"])

    def test_bridge_routes_matching_plugin_and_falls_back_on_null(self) -> None:
        plugins = [
            {
                "name": "browser-tools",
                "description": "Open and test local websites.",
                "skills": ["browser"],
                "capability_text": "browser open test local websites localhost screenshot",
                "manifest": "plugin.json",
            }
        ]

        matched = front_door.choose_plugin_route(
            "Open localhost and take a screenshot",
            plugins,
        )
        fallback = front_door.complete_plugin_route(matched, None)

        self.assertEqual(matched["plugin"], "browser-tools")
        self.assertTrue(matched["matched"])
        self.assertEqual(fallback["source"], "acc")
        self.assertEqual(fallback["reason"], "plugin-returned-no-result")

    def test_front_door_uses_plugin_route_and_keeps_acc_fallback(self) -> None:
        plugins = [
            {
                "name": "browser-tools",
                "description": "Open and inspect local websites.",
                "skills": ["browser"],
                "capability_text": "browser open inspect localhost screenshot",
                "manifest": "plugin.json",
            }
        ]

        result = front_door.route_request(
            "Open localhost and take a screenshot",
            plugins=plugins,
        )

        self.assertEqual(result["route"], ["plugin:browser-tools"])
        self.assertEqual(result["fallback_route"], ["intake", "checklist", "plan"])

    def test_bridge_does_not_route_weak_or_self_matches(self) -> None:
        plugins = [
            {
                "name": "anyone-can-code",
                "description": "General builder workflow.",
                "skills": ["orchestrator"],
                "capability_text": "general builder workflow orchestrator",
                "manifest": "plugin.json",
            },
            {
                "name": "spreadsheets",
                "description": "Create and edit spreadsheets.",
                "skills": ["spreadsheets"],
                "capability_text": "create edit spreadsheets workbook csv",
                "manifest": "plugin.json",
            },
        ]

        result = front_door.choose_plugin_route("Fix the login bug", plugins)

        self.assertFalse(result["matched"])
        self.assertEqual(result["source"], "acc")

    def test_live_cache_does_not_route_generic_bug_to_workflow_plugin(self) -> None:
        result = front_door.choose_plugin_route(
            "Fix the login crash",
            front_door.scan_installed_plugins(),
        )

        self.assertFalse(result["matched"])
        self.assertEqual(result["source"], "acc")

    def test_live_cache_does_not_capture_generic_feature_request(self) -> None:
        result = front_door.route_request(
            "Add password reset to this existing repo",
        )

        self.assertEqual(result["entry_mode"], "feature-request")
        self.assertFalse(result["bridge"]["matched"])
        self.assertEqual(result["route"], ["plan", "execute", "verify"])

    def test_doctor_smoke_contract(self) -> None:
        ok, evidence = front_door.smoke_check()

        self.assertTrue(ok)
        self.assertIn("plugin fallback ready", evidence)


if __name__ == "__main__":
    unittest.main()
