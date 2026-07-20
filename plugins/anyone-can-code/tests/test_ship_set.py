#!/usr/bin/env python3
"""Ship-set discipline (Superpowers packaging lessons; ACC keeps real hooks).

Locks list-ready plugin shape without dropping hooks or skills.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
HOOKS = PLUGIN / "hooks" / "hooks.json"
MCP = PLUGIN / ".mcp.json"
SKILLS = PLUGIN / "skills"

# Spine skills that must carry HARD-GATE + red-flag discipline.
SPINE = ("plan", "execute", "verify")

REQUIRED_INTERFACE = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
)


class ShipSetTests(unittest.TestCase):
    def test_manifest_is_list_ready(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("name"), "anyone-can-code")
        self.assertTrue(manifest.get("version"))
        self.assertTrue(manifest.get("description"))
        # ACC product: real hooks forever — never Superpowers empty object.
        self.assertEqual(manifest.get("hooks"), "./hooks/hooks.json")
        self.assertNotEqual(manifest.get("hooks"), {})
        self.assertEqual(manifest.get("skills"), "./skills/")
        self.assertEqual(manifest.get("mcpServers"), "./.mcp.json")
        interface = manifest.get("interface") or {}
        for key in REQUIRED_INTERFACE:
            self.assertIn(key, interface, f"interface missing {key}")
        prompts = interface.get("defaultPrompt") or []
        self.assertLessEqual(len(prompts), 3)
        for p in prompts:
            self.assertLessEqual(len(p), 128, p)

    def test_hooks_file_exists_and_is_not_empty_object(self) -> None:
        self.assertTrue(HOOKS.is_file())
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        events = data.get("hooks") or {}
        self.assertIsInstance(events, dict)
        self.assertGreaterEqual(len(events), 8)
        self.assertIn("SessionStart", events)
        self.assertIn("Stop", events)
        # Every command uses Codex ${PLUGIN_ROOT} + Windows override.
        for event, groups in events.items():
            for group in groups:
                for hook in group.get("hooks") or []:
                    if hook.get("type", "command") != "command":
                        continue
                    with self.subTest(event=event):
                        self.assertIn("${PLUGIN_ROOT}", hook.get("command", ""))
                        self.assertIn(
                            "${PLUGIN_ROOT}", hook.get("commandWindows", "")
                        )
                        self.assertIn("timeout", hook)

    def test_mcp_manifest_valid(self) -> None:
        self.assertTrue(MCP.is_file())
        data = json.loads(MCP.read_text(encoding="utf-8"))
        # File is the server map itself (not nested under mcpServers).
        self.assertIsInstance(data, dict)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("memory", data)

    def test_marketplace_one_plugin_path(self) -> None:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        plugins = data.get("plugins") or []
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0].get("name"), "anyone-can-code")
        source = plugins[0].get("source") or {}
        self.assertEqual(source.get("path"), "./plugins/anyone-can-code")

    def test_every_skill_has_skill_md_and_openai_yaml(self) -> None:
        skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
        self.assertGreaterEqual(len(skill_dirs), 10)
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                skill_md = skill_dir / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                text = skill_md.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---"), skill_dir.name)
                self.assertIn("name:", text)
                self.assertIn("description:", text)
                # Trigger-first Superpowers shape: description starts with Use …
                fm = text.split("---", 2)[1]
                desc_line = next(
                    (
                        line
                        for line in fm.splitlines()
                        if line.strip().startswith("description:")
                    ),
                    "",
                )
                self.assertRegex(
                    desc_line,
                    r'description:\s*"Use\s',
                    f"{skill_dir.name} description must start with Use …",
                )
                yaml_path = skill_dir / "agents" / "openai.yaml"
                self.assertTrue(yaml_path.is_file(), f"missing {yaml_path}")
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                self.assertIn("interface", data)

    def test_spine_skills_have_hard_gate_and_red_flags(self) -> None:
        for name in SPINE:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=name):
                self.assertIn("HARD-GATE", text)
                self.assertIn("Red flags", text)
                self.assertIn("Done — back to normal", text)
                self.assertIn("Next skill", text)
                # Progressive detail path exists
                refs = SKILLS / name / "references"
                self.assertTrue(refs.is_dir(), f"{name} missing references/")
                self.assertTrue(any(refs.glob("*.md")), f"{name} empty references/")

    def test_hooks_key_never_omitted_while_shipping_hooks_dir(self) -> None:
        """Mono-repo trap: missing hooks key can auto-load wrong hooks.

        ACC must always set explicit hooks path when hooks/ exists.
        """
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue((PLUGIN / "hooks").is_dir())
        self.assertIn("hooks", manifest)
        self.assertEqual(manifest["hooks"], "./hooks/hooks.json")


if __name__ == "__main__":
    unittest.main()
