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

    def test_existing_website_improvement_is_not_routed_as_new_idea(self) -> None:
        result = front_door.route_request(
            "Improve the existing website until it is a perfect demo site "
            "using ACC, brainstorming, product design, and UI skills",
            plugins=[],
        )

        self.assertEqual(result["entry_mode"], "polish-review")
        self.assertEqual(result["product_type"], "website")
        self.assertEqual(result["banner"], "Detected: polish-review + website")
        self.assertEqual(result["route"], ["review", "polish", "verify"])
        self.assertNotIn("intake", result)

    def test_every_route_requires_visible_useful_turn_completion(self) -> None:
        requests = (
            "I want to build a website",
            "Fix the login crash",
            "Improve the existing website",
        )

        for request in requests:
            with self.subTest(request=request):
                result = front_door.route_request(request, plugins=[])
                contract = result["response_contract"]
                self.assertTrue(contract["visible_text_required"])
                self.assertTrue(contract["next_action_required"])
                self.assertEqual(contract["empty_result_action"], "acc-fallback-response")
                self.assertIn("summary", contract["required_fields"])
                self.assertIn("next_action", contract["required_fields"])

    def test_every_route_requires_memory_preflight_before_first_action(self) -> None:
        result = front_door.route_request(
            "Use the plugin again after update and remember prior mistakes",
            {"project_root": "C:/project"},
            plugins=[],
        )

        preflight = result["memory_preflight"]
        self.assertTrue(preflight["required"])
        self.assertEqual(preflight["source"], "portable-markdown")
        self.assertEqual(preflight["script"], "scripts/memory_preflight.py")
        self.assertEqual(preflight["visible_line_prefix"], "Relevant memory used:")
        self.assertEqual(preflight["project_root"], "C:/project")
        self.assertIn("ask-question", preflight["required_before"])
        self.assertIn("route-specialist", preflight["required_before"])
        self.assertIn("tool-action", preflight["required_before"])

    def test_requirement_change_still_requires_memory_preflight(self) -> None:
        result = front_door.route_request(
            "Actually update the plugin and reuse the mistake",
            {"workflow_active": True, "resume_step": "execute", "project_root": "C:/project"},
            plugins=[],
        )

        self.assertEqual(result["entry_mode"], "requirement-change")
        self.assertTrue(result["memory_preflight"]["required"])
        self.assertEqual(result["memory_preflight"]["project_root"], "C:/project")

    def test_orchestrator_enforces_visible_response_contract(self) -> None:
        skill_text = (
            PLUGIN_ROOT / "skills" / "orchestrator" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("response_contract", skill_text)
        self.assertIn("Never end a meaningful routed turn without visible text", skill_text)
        self.assertIn("Codex Desktop rendering", skill_text)
        self.assertIn("Relevant memory used:", skill_text)
        self.assertIn("memory_preflight", skill_text)

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
        self.assertEqual(matched["health"]["status"], "healthy")
        self.assertFalse(matched["durable_truth"])
        self.assertEqual(fallback["source"], "acc")
        self.assertEqual(fallback["reason"], "plugin-returned-no-result")
        self.assertEqual(fallback["fallback"]["owner"], "acc")

    def test_capability_probe_blocks_unhealthy_plugin_and_uses_acc_fallback(self) -> None:
        probes = []

        def unhealthy_probe(plugin):
            probes.append(plugin["name"])
            return {"status": "unhealthy", "reason": "service unavailable"}

        result = front_door.choose_plugin_route(
            "Open localhost and take a screenshot",
            [
                {
                    "name": "browser-tools",
                    "description": "Open and inspect local websites.",
                    "skills": ["browser"],
                    "capability_text": "browser open inspect localhost screenshot",
                    "manifest": "plugin.json",
                    "health_probe": unhealthy_probe,
                }
            ],
        )

        self.assertEqual(probes, ["browser-tools"])
        self.assertFalse(result["matched"])
        self.assertEqual(result["reason"], "capability-unhealthy")
        self.assertEqual(result["health"]["status"], "unhealthy")
        self.assertEqual(result["fallback"]["owner"], "acc")
        self.assertFalse(result["durable_truth"])

    def test_capability_runtime_failure_returns_to_acc(self) -> None:
        decision = front_door.choose_plugin_route(
            "Open localhost and take a screenshot",
            [
                {
                    "name": "browser-tools",
                    "description": "Open and inspect local websites.",
                    "skills": ["browser"],
                    "capability_text": "browser open inspect localhost screenshot",
                    "manifest": "plugin.json",
                }
            ],
        )

        result = front_door.complete_plugin_route(
            decision,
            {"status": "failed", "reason": "browser did not start"},
        )

        self.assertFalse(result["matched"])
        self.assertEqual(result["source"], "acc")
        self.assertEqual(result["reason"], "capability-runtime-failure")
        self.assertEqual(result["workflow_owner"], "acc")
        self.assertFalse(result["durable_truth"])

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

        self.assertEqual(result["workflow_owner"], "acc")
        self.assertEqual(result["route"], ["intake", "checklist", "plan"])
        self.assertEqual(result["fallback_route"], ["intake", "checklist", "plan"])
        assignment = result["bridge"]["assignment"]
        self.assertEqual(assignment["specialist"], "browser-tools")
        self.assertEqual(assignment["workflow_owner"], "acc")
        self.assertEqual(assignment["return_to"], "acc")
        self.assertIn("create-controlling-plan", assignment["forbidden_actions"])

    def test_specialist_takeover_is_blocked_and_technical_result_is_kept(self) -> None:
        decision = {
            "matched": True,
            "source": "plugin",
            "plugin": "design-tools",
            "capability": "UI design",
            "reason": "installed-manifest-match",
        }
        assignment = front_door.build_specialist_assignment(
            decision,
            request="Improve this page",
            allowed_output="UI recommendations",
        )

        result = front_door.complete_plugin_route(
            {**decision, "assignment": assignment},
            {
                "technical_result": ["Increase contrast"],
                "workflow_owner": "design-tools",
                "plan": "Use the plugin plan",
                "commit_required": True,
            },
        )

        self.assertEqual(result["source"], "plugin")
        self.assertEqual(result["workflow_owner"], "acc")
        self.assertEqual(result["result"], ["Increase contrast"])
        self.assertTrue(result["takeover_blocked"])
        self.assertCountEqual(
            result["blocked_controls"],
            ["workflow_owner", "plan", "commit_required"],
        )

    def test_specialist_mentions_do_not_imply_workflow_handoff(self) -> None:
        result = front_door.route_request(
            "Use ACC, brainstorming, Product Design, and UI skills to improve "
            "the existing website",
            plugins=[],
        )

        self.assertEqual(result["workflow_owner"], "acc")
        contract = result["workflow_contract"]
        self.assertTrue(contract["explicit_handoff_required"])
        self.assertTrue(contract["load_project_context_first"])
        self.assertEqual(contract["specialist_process"], "advisory")
        self.assertFalse(contract["specialist_may_change_route"])

    def test_requested_specialists_are_all_accounted_for(self) -> None:
        plugins = [
            {
                "name": "product-design",
                "description": "Product Design UI prototyping and visual direction.",
                "skills": ["get-context", "image-to-code"],
                "capability_text": "product design ui prototyping visual direction",
                "manifest": "plugin.json",
            }
        ]

        result = front_door.route_request(
            "Use ACC, brainstorming, Product Design, and UI skills to improve "
            "the existing website",
            plugins=plugins,
        )

        requested = {
            item["requested"]: item
            for item in result["requested_specialists"]
        }
        self.assertIn("brainstorming", requested)
        self.assertIn("product design", requested)
        self.assertIn("ui skills", requested)
        self.assertFalse(requested["brainstorming"]["matched"])
        self.assertEqual(
            requested["brainstorming"]["reason"],
            "requested-specialist-unavailable",
        )
        self.assertTrue(requested["product design"]["matched"])
        self.assertEqual(requested["product design"]["plugin"], "product-design")
        self.assertTrue(requested["ui skills"]["matched"])
        self.assertEqual(requested["ui skills"]["plugin"], "product-design")
        self.assertEqual(requested["brainstorming"]["fallback"]["owner"], "acc")
        self.assertEqual(result["workflow_owner"], "acc")

    def test_requested_specialist_unhealthy_falls_back_plainly(self) -> None:
        result = front_door.route_request(
            "Use Product Design to improve this website",
            plugins=[
                {
                    "name": "product-design",
                    "description": "Product Design UI help.",
                    "skills": ["get-context"],
                    "capability_text": "product design ui",
                    "manifest": "plugin.json",
                    "health": "unhealthy",
                    "health_reason": "not installed correctly",
                }
            ],
        )

        specialist = result["requested_specialists"][0]
        self.assertEqual(specialist["requested"], "product design")
        self.assertFalse(specialist["matched"])
        self.assertEqual(specialist["plugin"], "product-design")
        self.assertEqual(specialist["reason"], "requested-specialist-unhealthy")
        self.assertEqual(specialist["health"]["reason"], "not installed correctly")
        self.assertEqual(specialist["fallback"]["owner"], "acc")

    def test_specialist_assignment_carries_prework_boundaries(self) -> None:
        decision = {
            "matched": True,
            "source": "plugin",
            "plugin": "design-tools",
            "capability": "UI design",
            "reason": "installed-manifest-match",
        }

        assignment = front_door.build_specialist_assignment(
            decision,
            request="Improve this existing website",
            allowed_output="UI recommendations",
        )

        self.assertTrue(assignment["load_project_context_first"])
        self.assertEqual(assignment["process_authority"], "advisory")
        self.assertIn("follow-project-preferences", assignment["permissions"])
        self.assertIn("offer-visual-companion", assignment["forbidden_actions"])
        self.assertIn("open-browser", assignment["forbidden_actions"])
        self.assertIn("start-server", assignment["forbidden_actions"])

    def test_nested_specialist_takeover_is_blocked_recursively(self) -> None:
        decision = {
            "matched": True,
            "source": "plugin",
            "plugin": "brainstorming-tools",
            "capability": "product brainstorming",
            "reason": "installed-manifest-match",
        }
        assignment = front_door.build_specialist_assignment(
            decision,
            request="Improve existing website",
            allowed_output="bounded design recommendations",
        )

        result = front_door.complete_plugin_route(
            {**decision, "assignment": assignment},
            {
                "technical_result": ["Keep current design", "Improve hierarchy"],
                "process": {
                    "plan": ["ask questions", "write external spec"],
                    "approval_gate": "wait for approval",
                    "visual_companion": True,
                    "browser_action": "open local URL",
                    "server_action": "start dev server",
                },
            },
        )

        self.assertEqual(
            result["result"],
            ["Keep current design", "Improve hierarchy"],
        )
        self.assertTrue(result["takeover_blocked"])
        self.assertCountEqual(
            result["blocked_control_paths"],
            [
                "process.plan",
                "process.approval_gate",
                "process.visual_companion",
                "process.browser_action",
                "process.server_action",
            ],
        )
        self.assertEqual(result["workflow_owner"], "acc")

    def test_nested_process_is_removed_when_result_has_no_technical_wrapper(self) -> None:
        decision = {
            "matched": True,
            "source": "plugin",
            "plugin": "design-tools",
            "capability": "UI design",
            "reason": "installed-manifest-match",
        }
        assignment = front_door.build_specialist_assignment(
            decision,
            request="Improve existing website",
            allowed_output="UI recommendations",
        )

        result = front_door.complete_plugin_route(
            {**decision, "assignment": assignment},
            {
                "recommendations": ["Increase contrast"],
                "process": {
                    "plan": "Replace ACC plan",
                    "response_style": "verbose",
                },
            },
        )

        self.assertEqual(result["result"], {"recommendations": ["Increase contrast"]})
        self.assertCountEqual(
            result["blocked_control_paths"],
            ["process.plan", "process.response_style"],
        )

    def test_explicit_user_handoff_allows_new_workflow_owner(self) -> None:
        decision = {
            "matched": True,
            "source": "plugin",
            "plugin": "design-tools",
            "capability": "UI design",
            "reason": "installed-manifest-match",
        }
        assignment = front_door.build_specialist_assignment(
            decision,
            request="Let design-tools own this workflow",
            allowed_output="full workflow",
            user_handoff=True,
        )

        self.assertEqual(assignment["workflow_owner"], "design-tools")
        self.assertTrue(assignment["user_handoff"])
        self.assertEqual(assignment["process_authority"], "owner")
        self.assertEqual(assignment["forbidden_actions"], [])

    def test_every_route_exposes_windows_command_guard(self) -> None:
        result = front_door.route_request(
            "Add password reset to this existing repo",
            {"os": "windows", "shell": "powershell", "repo_root": "C:/repo"},
            plugins=[],
        )

        guard = result["command_guard"]
        self.assertTrue(guard["required"])
        self.assertTrue(guard["windows"])
        self.assertEqual(guard["shell"], "powershell")
        self.assertEqual(guard["package_runner"], "npm.cmd")
        self.assertIn("git-command", guard["required_before"])
        self.assertEqual(guard["cwd_rule"], "resolve-repo-root-before-git")

    def test_every_route_exposes_high_usage_checkpoint(self) -> None:
        result = front_door.route_request(
            "Add password reset to this existing repo",
            {"primary_usage_percent": 90},
            plugins=[],
        )

        checkpoint = result["usage_checkpoint"]
        self.assertTrue(checkpoint["required"])
        self.assertEqual(checkpoint["checkpoint_threshold_percent"], 85)
        self.assertEqual(checkpoint["split_threshold_percent"], 90)
        self.assertEqual(checkpoint["stop_threshold_percent"], 94)
        self.assertEqual(checkpoint["current"]["action"], "split")
        self.assertIn("checkpoint", checkpoint["required_before"])

    def test_every_route_exposes_patch_retry_policy(self) -> None:
        result = front_door.route_request(
            "Patch the existing repo",
            {"failed_patch_attempts": 1, "last_patch_failed": True},
            plugins=[],
        )

        policy = result["patch_retry"]
        self.assertTrue(policy["required"])
        self.assertEqual(policy["max_failed_attempts"], 2)
        self.assertEqual(policy["current"]["action"], "reread-exact-target")
        self.assertFalse(policy["current"]["can_apply_patch"])
        self.assertIn("failed-patch", policy["required_after"])

    def test_every_route_exposes_mechanics_docs_gate(self) -> None:
        result = front_door.route_request(
            "Change Codex Desktop hook launch behavior on Windows",
            {},
            plugins=[],
        )

        gate = result["mechanics_docs_gate"]
        self.assertTrue(gate["required"])
        self.assertEqual(gate["current"]["action"], "write-docs-brief")
        self.assertFalse(gate["current"]["can_change_code"])
        self.assertIn("platform-mechanics-change", gate["required_before"])

    def test_windows_command_guard_rejects_npm_ps1_and_bash_or(self) -> None:
        assessment = front_door.assess_command_guidance(
            "npm test || npm run build",
            {"os": "windows", "shell": "powershell", "repo_root": "C:/repo"},
        )

        self.assertFalse(assessment["safe"])
        self.assertIn("powershell-npm-ps1", assessment["violations"])
        self.assertIn("powershell-bash-or", assessment["violations"])
        self.assertIn("npm.cmd", assessment["recommended"])
        self.assertIn("$LASTEXITCODE", assessment["recommended"])

    def test_git_guidance_requires_resolved_repo_root(self) -> None:
        unsafe = front_door.assess_command_guidance(
            "git status",
            {"os": "windows", "shell": "powershell", "project_root": "C:/workspace"},
        )
        safe = front_door.assess_command_guidance(
            "git status",
            {"os": "windows", "shell": "powershell", "repo_root": "C:/repo"},
        )

        self.assertFalse(unsafe["safe"])
        self.assertIn("git-root-required", unsafe["violations"])
        self.assertIn("C:/repo", safe["cwd"])
        self.assertTrue(safe["safe"])

    def test_command_guard_docs_are_required(self) -> None:
        for skill in ("orchestrator", "bridge", "status", "verify"):
            with self.subTest(skill=skill):
                skill_text = (
                    PLUGIN_ROOT / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("command_guard", skill_text)
                self.assertIn("npm.cmd", skill_text)
                self.assertIn("repo root", skill_text)

    def test_high_usage_checkpoint_docs_are_required(self) -> None:
        for skill in ("orchestrator", "status", "resume", "verify"):
            with self.subTest(skill=skill):
                skill_text = (
                    PLUGIN_ROOT / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("usage_checkpoint", skill_text)
                self.assertIn("85%", skill_text)
                self.assertIn("90%", skill_text)
                self.assertIn("94%", skill_text)

    def test_patch_retry_docs_are_required(self) -> None:
        for skill in ("orchestrator", "execute", "status", "verify"):
            with self.subTest(skill=skill):
                skill_text = (
                    PLUGIN_ROOT / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("patch_retry", skill_text)
                self.assertIn("failed patch", skill_text)
                self.assertIn("reread", skill_text)

    def test_mechanics_docs_gate_docs_are_required(self) -> None:
        for skill in ("orchestrator", "plan", "execute", "status", "verify"):
            with self.subTest(skill=skill):
                skill_text = (
                    PLUGIN_ROOT / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("mechanics_docs_gate", skill_text)
                self.assertIn("docs brief", skill_text)
                self.assertIn("platform mechanics", skill_text)
        for rel in ("README.md", "VALIDATION.md"):
            with self.subTest(doc=rel):
                text = (PLUGIN_ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("mechanics_docs_gate", text)
                self.assertIn("docs brief", text)

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
        self.assertIn("capability probe and fallback ready", evidence)
        self.assertIn("ownership containment ready", evidence)


if __name__ == "__main__":
    unittest.main()
