#!/usr/bin/env python3
"""Host detect is wording-only and never invents undocumented Codex APIs."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import host_detect as hd  # noqa: E402


class HostDetectTests(unittest.TestCase):
    def test_forced_acc_host(self) -> None:
        self.assertEqual(hd.detect_host({"ACC_HOST": "cli"}), "cli")
        self.assertEqual(hd.detect_host({"ACC_HOST": "desktop"}), "desktop")
        self.assertEqual(hd.detect_host({"ACC_HOST": "unknown"}), "unknown")

    def test_desktop_markers(self) -> None:
        self.assertEqual(hd.detect_host({"CODEX_DESKTOP": "1"}), "desktop")
        self.assertEqual(hd.detect_host({"CODEX_APP": "true"}), "desktop")

    def test_cli_markers(self) -> None:
        self.assertEqual(hd.detect_host({"CODEX_CLI": "1"}), "cli")
        self.assertEqual(hd.detect_host({"CODEX_TUI": "yes"}), "cli")

    def test_empty_env_is_unknown_or_safe(self) -> None:
        # Empty env + no tty simulation: unknown
        result = hd.detect_host({})
        self.assertIn(result, {"cli", "desktop", "unknown"})

    def test_guidance_keys(self) -> None:
        for host in ("cli", "desktop", "unknown"):
            g = hd.host_guidance(host)
            self.assertEqual(g["host"], host)
            for key in ("install", "review", "long_job", "model", "sites", "scheduled"):
                self.assertTrue(str(g[key]).strip())


if __name__ == "__main__":
    unittest.main()
