#!/usr/bin/env python3
"""Codex hook matchers must use real tool names (hooks docs)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
HOOKS = PLUGIN / "hooks" / "hooks.json"


class HookMatcherTests(unittest.TestCase):
    def test_tool_events_match_bash_and_apply_patch(self) -> None:
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        for event in ("PreToolUse", "PostToolUse", "PermissionRequest"):
            groups = data["hooks"][event]
            matchers = [g.get("matcher") or "" for g in groups]
            joined = " ".join(matchers)
            with self.subTest(event=event):
                self.assertIn("Bash", joined)
                self.assertIn("apply_patch", joined)
                # Dead Claude-only names without apply_patch are not enough.
                self.assertNotEqual(joined.strip(), "Edit|Write")


if __name__ == "__main__":
    unittest.main()
