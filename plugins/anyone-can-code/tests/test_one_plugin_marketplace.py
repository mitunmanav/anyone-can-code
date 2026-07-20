#!/usr/bin/env python3
"""One Codex plugin for Desktop + CLI (Superpowers model)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
HOOKS = PLUGIN / "hooks" / "hooks.json"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"


class OnePluginMarketplaceTests(unittest.TestCase):
    def test_marketplace_lists_only_anyone_can_code(self) -> None:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        names = [p.get("name") for p in data.get("plugins") or []]
        self.assertEqual(names, ["anyone-can-code"])

    def test_manifest_points_at_hooks_and_skills(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("name"), "anyone-can-code")
        self.assertEqual(manifest.get("hooks"), "./hooks/hooks.json")
        self.assertEqual(manifest.get("skills"), "./skills/")

    def test_hooks_are_cross_host_plugin_root(self) -> None:
        hooks = json.loads(HOOKS.read_text(encoding="utf-8"))
        events = set(hooks.get("hooks") or {})
        self.assertIn("SessionStart", events)
        self.assertIn("PreToolUse", events)
        for event, groups in (hooks.get("hooks") or {}).items():
            for group in groups:
                for hook in group.get("hooks") or []:
                    if hook.get("type", "command") != "command":
                        continue
                    with self.subTest(event=event):
                        self.assertIn("$PLUGIN_ROOT", hook.get("command", ""))
                        self.assertIn("%PLUGIN_ROOT%", hook.get("commandWindows", ""))
                        self.assertIn("timeout", hook)


if __name__ == "__main__":
    unittest.main()
