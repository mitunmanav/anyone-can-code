"""Portable cross-tool handoff — product path + format rules."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
HOOKS = PLUGIN_ROOT / "hooks" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HOOKS))

import portable_handoff  # noqa: E402
import build_handoff  # noqa: E402
import canonical_state  # noqa: E402


class PortableHandoffWriter(unittest.TestCase):
    def test_writes_required_headers_and_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_state.update_canonical_state(
                root,
                {
                    "active_goal": "Ship handoff",
                    "active_task": "Write portable file",
                    "next_action": "Wire save_session",
                    "plan": [
                        {"text": "Design format", "done": True},
                        {"text": "Implement writer", "done": False},
                    ],
                },
            )
            result = portable_handoff.write_portable_handoff(
                root,
                tool_left="codex-desktop",
                session_id="thr_test_123",
                summary="Stopped mid wire",
            )
            self.assertTrue(result["written"])
            path = Path(result["path"])
            self.assertTrue(path.is_file())
            self.assertIn("PORTABLE_HANDOFF.md", str(path))
            self.assertNotIn("/docs/", str(path))
            text = path.read_text(encoding="utf-8")
            for needle in (
                "schema: acc-portable-handoff/1",
                "## Goal",
                "## Plan",
                "## State",
                "## Memory",
                "## Next step",
                "## How to resume",
                "Ship handoff",
                "Wire save_session",
                "codex resume",
                "thread/resume",
                "thread/start",
            ):
                self.assertIn(needle, text)
            # resume-note mirror
            note = root / ".codex/anyone-can-code/artifacts/resume-note.md"
            self.assertTrue(note.is_file())
            self.assertIn("PORTABLE_HANDOFF", note.read_text(encoding="utf-8"))

    def test_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_state.update_canonical_state(
                root,
                {
                    "active_goal": "goal",
                    "next_action": "continue",
                    "active_task": "api_key=sk-abcdefghijklmnopqrstuvwxyz123456",
                },
            )
            portable_handoff.write_portable_handoff(
                root,
                summary="password: hunter2secret99 and Bearer abcdefghijklmnop",
            )
            text = portable_handoff.read_portable_handoff(root)
            self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", text)
            self.assertIn("[REDACTED]", text)

    def test_size_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            huge = "x" * 50_000
            canonical_state.update_canonical_state(
                root,
                {"active_goal": huge, "next_action": "done", "active_task": huge},
            )
            portable_handoff.write_portable_handoff(root, summary=huge)
            raw = portable_handoff.portable_path(root).read_bytes()
            self.assertLessEqual(len(raw), portable_handoff.MAX_BYTES + 50)

    def test_idempotent_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_state.update_canonical_state(
                root, {"active_goal": "g", "next_action": "n1"}
            )
            portable_handoff.write_portable_handoff(root)
            first = portable_handoff.read_portable_handoff(root)
            canonical_state.update_canonical_state(root, {"next_action": "n2"})
            portable_handoff.write_portable_handoff(root)
            second = portable_handoff.read_portable_handoff(root)
            self.assertIn("n2", second)
            self.assertIn("schema: acc-portable-handoff/1", second)
            self.assertIn("## Goal", first)

    def test_skip_empty_idle_keeps_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_state.update_canonical_state(
                root, {"active_goal": "keep me", "next_action": "important"}
            )
            portable_handoff.write_portable_handoff(root)
            # empty state overwrite attempt
            empty = canonical_state.read_canonical_state(root)
            empty["active_goal"] = ""
            empty["active_task"] = ""
            empty["next_action"] = ""
            result = portable_handoff.write_portable_handoff(
                root, empty, summary="", skip_if_empty=True
            )
            self.assertTrue(result.get("skipped"))
            self.assertIn("keep me", portable_handoff.read_portable_handoff(root))


class BuildHandoffWritesFile(unittest.TestCase):
    def test_cli_writes_portable_and_prints_prompt(self):
        script = SCRIPTS / "build_handoff.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r = subprocess.run(
                [sys.executable, str(script), "--project-root", str(root)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("PORTABLE_HANDOFF", r.stdout)
            self.assertIn("thread/start", r.stdout)
            self.assertTrue(
                (root / ".codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md").is_file()
            )

    def test_stdout_only_does_not_require_write(self):
        script = SCRIPTS / "build_handoff.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--project-root",
                    str(root),
                    "--stdout-only",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Active goal", r.stdout)


class LoadSessionInjectsPortable(unittest.TestCase):
    def test_inject_in_context(self):
        import load_session
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state.ensure_project_layout(root)
            canonical_state.update_canonical_state(
                root,
                {
                    "active_goal": "Cross tool resume",
                    "next_action": "Open portable file",
                },
            )
            portable_handoff.write_portable_handoff(root)
            ctx = load_session.build_context(root, "startup")
            self.assertIn("Portable handoff", ctx)
            self.assertIn("Cross tool resume", ctx)
            self.assertIn("Open portable file", ctx)


class SaveSessionWritesPortable(unittest.TestCase):
    def test_stop_writes_portable(self):
        import save_session
        import state

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state.ensure_project_layout(root)
            canonical_state.update_canonical_state(
                root, {"active_goal": "goal", "next_action": "step"}
            )
            payload = {
                "session_id": "sess_abc",
                "turn_id": "turn_1",
                "last_assistant_message": "Did work. Next: run tests.",
            }
            # Use real handle path pieces
            workflow = state.read_state(root)
            save_session.write_resume_artifacts(
                root, payload, "Did work. Next: run tests.", workflow
            )
            path = root / ".codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md"
            self.assertTrue(path.is_file(), "live Stop path must write portable file")
            text = path.read_text(encoding="utf-8")
            self.assertIn("sess_abc", text)


class SkillDocsNative(unittest.TestCase):
    def test_skills_mention_native_resume_not_fake_create_thread(self):
        handoff = (PLUGIN_ROOT / "skills/handoff/SKILL.md").read_text(encoding="utf-8")
        resume = (PLUGIN_ROOT / "skills/resume/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("codex resume", handoff)
        self.assertIn("thread/start", handoff)
        self.assertIn("PORTABLE_HANDOFF", handoff)
        self.assertNotIn("create_thread", handoff)
        self.assertIn("PORTABLE_HANDOFF", resume)
        self.assertIn("codex resume", resume)


if __name__ == "__main__":
    unittest.main()
