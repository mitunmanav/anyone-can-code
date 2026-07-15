#!/usr/bin/env python3
"""CLI port: hooks must be portable + timed (docs: omit timeout → 600s)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
HOOKS = PLUGIN / "hooks" / "hooks.json"
MAX_TIMEOUT = 60


def iter_command_hooks():
    data = json.loads(HOOKS.read_text(encoding="utf-8"))
    for event, groups in data["hooks"].items():
        for gi, group in enumerate(groups):
            for hi, hook in enumerate(group.get("hooks") or []):
                if hook.get("type", "command") != "command":
                    continue
                yield event, gi, hi, hook


class CliHooksPortTests(unittest.TestCase):
    def test_every_command_hook_has_short_timeout(self) -> None:
        for event, gi, hi, hook in iter_command_hooks():
            with self.subTest(event=event, group=gi, hook=hi):
                self.assertIn("timeout", hook, "timeout required (docs default 600s if missing)")
                self.assertIsInstance(hook["timeout"], int)
                self.assertGreater(hook["timeout"], 0)
                self.assertLessEqual(hook["timeout"], MAX_TIMEOUT)

    def test_portable_command_does_not_require_powershell(self) -> None:
        for event, gi, hi, hook in iter_command_hooks():
            with self.subTest(event=event, group=gi, hook=hi):
                cmd = hook.get("command") or ""
                self.assertTrue(cmd.strip(), "command required")
                low = cmd.lower()
                self.assertNotIn("powershell", low)
                self.assertNotIn("encodedcommand", low)
                self.assertIn("PLUGIN_ROOT", cmd)
                self.assertTrue(
                    "python" in low or "py " in low or low.startswith("py"),
                    f"portable command should invoke python: {cmd!r}",
                )

    def test_command_windows_is_string_when_present(self) -> None:
        for event, gi, hi, hook in iter_command_hooks():
            with self.subTest(event=event, group=gi, hook=hi):
                if "commandWindows" not in hook:
                    continue
                self.assertIsInstance(hook["commandWindows"], str)
                self.assertTrue(hook["commandWindows"].strip())

    def test_event_script_map_covers_all_events(self) -> None:
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        expected = {
            "SessionStart": "load_session.py",
            "UserPromptSubmit": "guard.py",
            "PreToolUse": "guard.py",
            "PermissionRequest": "audit.py",
            "PostToolUse": "audit.py",
            "Stop": "save_session.py",
            "PreCompact": "compact.py",
            "SubagentStart": "subagent.py",
            "SubagentStop": "subagent.py",
            "PostCompact": "compact.py",
        }
        for event, script in expected.items():
            with self.subTest(event=event):
                self.assertIn(event, data["hooks"])
                cmd = data["hooks"][event][0]["hooks"][0]["command"]
                self.assertIn(script, cmd)


if __name__ == "__main__":
    unittest.main()
