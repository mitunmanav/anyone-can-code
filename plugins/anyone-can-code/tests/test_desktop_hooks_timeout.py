#!/usr/bin/env python3
"""Desktop hooks: timeout required (Codex docs default 600s if omitted)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
HOOKS = PLUGIN / "hooks" / "hooks.json"
MAX_TIMEOUT = 60


class DesktopHooksTimeoutTests(unittest.TestCase):
    def test_every_command_hook_has_short_timeout(self) -> None:
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        for event, groups in data["hooks"].items():
            for gi, group in enumerate(groups):
                for hi, hook in enumerate(group.get("hooks") or []):
                    if hook.get("type", "command") != "command":
                        continue
                    with self.subTest(event=event, group=gi, hook=hi):
                        self.assertIn(
                            "timeout",
                            hook,
                            "timeout required (docs default 600s if missing)",
                        )
                        self.assertIsInstance(hook["timeout"], int)
                        self.assertGreater(hook["timeout"], 0)
                        self.assertLessEqual(hook["timeout"], MAX_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
