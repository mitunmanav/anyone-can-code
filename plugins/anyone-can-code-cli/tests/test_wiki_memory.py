"""Karpathy wiki layer: raw + notes + index.md + log.md. No native Codex memory."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import wiki_memory  # noqa: E402


def load_memory_server():
    path = PLUGIN_ROOT / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("acc_memory_server_wiki", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WikiMemoryUnitTests(unittest.TestCase):
    def test_layout_seeds_index_and_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = wiki_memory.ensure_wiki_layout(root)
            self.assertTrue(layout["raw"].is_dir())
            self.assertTrue(layout["wiki"].is_dir())
            self.assertTrue(layout["index_md"].is_file())
            self.assertTrue(layout["log_md"].is_file())
            self.assertIn("Pages", layout["index_md"].read_text(encoding="utf-8"))

    def test_store_sync_updates_index_and_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            notes = root / "notes" / "project"
            notes.mkdir(parents=True)
            note = notes / "decision-auth.md"
            note.write_text(
                "---\n"
                "id: n1\n"
                "kind: decision\n"
                "scope: project\n"
                "status: active\n"
                "---\n"
                "# Use JWT\n\n"
                "## Summary\n\n"
                "Use JWT for auth\n\n"
                "## Evidence\n\n"
                "Founder said so\n",
                encoding="utf-8",
            )
            result = wiki_memory.sync_after_store(root, "Use JWT for auth", kind="decision")
            index_text = (root / "wiki" / "index.md").read_text(encoding="utf-8")
            log_text = (root / "wiki" / "log.md").read_text(encoding="utf-8")
            self.assertTrue(result["index"]["rebuilt"])
            self.assertIn("Use JWT for auth", index_text)
            self.assertIn("save", log_text)
            brief = wiki_memory.session_brief(root)
            self.assertIn("Wiki brief", brief)
            self.assertIn("JWT", brief)

    def test_ingest_raw_requires_consent_and_never_overwrites_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = Path(tmp) / "source.txt"
            src.write_text("secret-plan-v1", encoding="utf-8")
            denied = wiki_memory.ingest_raw(root, src, consent=False)
            self.assertFalse(denied["ok"])
            first = wiki_memory.ingest_raw(root, src, consent=True)
            self.assertTrue(first["ok"])
            self.assertFalse(first["skipped"])
            dest = Path(first["path"])
            self.assertTrue(dest.is_file())
            self.assertTrue(str(dest).startswith(str(root / "raw")))
            second = wiki_memory.ingest_raw(root, src, consent=True)
            self.assertTrue(second["skipped"])
            # raw bytes unchanged
            self.assertEqual(dest.read_text(encoding="utf-8"), "secret-plan-v1")

    def test_lint_empty_and_orphan_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = wiki_memory.lint_wiki(root)
            self.assertGreaterEqual(empty["issue_count"], 1)
            codes = {i["code"] for i in empty["issues"]}
            self.assertIn("empty_wiki", codes)

            notes = root / "notes" / "project"
            notes.mkdir(parents=True)
            (notes / "a.md").write_text(
                "---\nkind: decision\nscope: project\nstatus: active\n---\n"
                "# A\n\n## Summary\n\nDecision A\n\n## Links\n\n[[missing-page]]\n",
                encoding="utf-8",
            )
            wiki_memory.rebuild_human_index(root)
            linted = wiki_memory.lint_wiki(root)
            codes2 = {i["code"] for i in linted["issues"]}
            self.assertIn("orphan_link", codes2)

    def test_stop_proposals_do_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki_memory.ensure_wiki_layout(root)
            prompt = wiki_memory.stop_save_prompt(
                [
                    "We decided to ship Desktop wiki first",
                    "ok",
                    "CLI comes after Desktop gate is green",
                ]
            )
            self.assertIn("Wiki save proposals", prompt)
            self.assertIn("Desktop wiki", prompt)
            # no extra note files created
            self.assertEqual(list((root / "notes").rglob("*.md")), [])


class WikiMcpIntegrationTests(unittest.TestCase):
    def test_store_feedback_writes_wiki_index(self) -> None:
        server = load_memory_server()
        with tempfile.TemporaryDirectory() as tmp:
            old = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                stored = server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "decision",
                        "summary": "Ship wiki memory on grok worktree only",
                        "confidence": 0.9,
                        "source": "test",
                        "project_root": str(Path(tmp) / "proj"),
                    }
                )
                self.assertTrue(stored["stored"])
                index_md = Path(tmp) / "wiki" / "index.md"
                log_md = Path(tmp) / "wiki" / "log.md"
                self.assertTrue(index_md.is_file())
                self.assertIn("Ship wiki memory", index_md.read_text(encoding="utf-8"))
                self.assertIn("save", log_md.read_text(encoding="utf-8"))
                brief = server.wiki_brief({"project_root": str(Path(tmp) / "proj")})
                self.assertFalse(brief["native_codex_memory"])
                self.assertIn("wiki", brief["brief"].lower() + "acc")
                lint = server.lint_wiki({"project_root": str(Path(tmp) / "proj")})
                self.assertGreaterEqual(lint["active_notes"], 1)
            finally:
                if old is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old

    def test_never_writes_codex_native_memories_path(self) -> None:
        server = load_memory_server()
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            fake_home.mkdir()
            data = Path(tmp) / "acc-data"
            data.mkdir()
            old_home = os.environ.get("HOME")
            old_data = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["HOME"] = str(fake_home)
            os.environ["ACC_MCP_DATA_ROOT"] = str(data)
            try:
                server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "lesson",
                        "summary": "Never touch native memories folder",
                        "source": "test",
                        "project_root": "/tmp/proj-wiki",
                    }
                )
                native = fake_home / ".codex" / "memories"
                self.assertFalse(native.exists())
                # ACC wrote only under ACC data root
                self.assertTrue(any(data.rglob("*.md")))
            finally:
                if old_home is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = old_home
                if old_data is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_data


class WikiHookTests(unittest.TestCase):
    def test_load_session_includes_wiki_brief(self) -> None:
        hooks = PLUGIN_ROOT / "hooks" / "scripts"
        sys.path.insert(0, str(hooks))
        import load_session  # type: ignore
        import state as hook_state  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            layout = hook_state.ensure_project_layout(repo)
            mem = layout["memory"]
            notes = mem / "notes" / "project"
            notes.mkdir(parents=True, exist_ok=True)
            (notes / "lesson1.md").write_text(
                "---\nkind: lesson\nscope: project\nstatus: active\n"
                "reinforcement_count: 3\n---\n"
                "# L\n\n## Summary\n\nAlways verify before done\n",
                encoding="utf-8",
            )
            wiki_memory.rebuild_human_index(mem)
            ctx = load_session.build_context(repo, "startup")
            self.assertIn("native Codex memories OFF", ctx)
            self.assertIn("Wiki brief", ctx)
            self.assertIn("verify before done", ctx.lower())

    def test_save_session_proposes_without_auto_wiki_when_no_signal(self) -> None:
        hooks = PLUGIN_ROOT / "hooks" / "scripts"
        sys.path.insert(0, str(hooks))
        import save_session  # type: ignore
        import state as hook_state  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            hook_state.ensure_project_layout(repo)
            result = save_session.handle_payload(
                {
                    "last_assistant_message": (
                        "We decided to keep wiki memory ACC-only on the grok branch."
                    ),
                    "turn_id": "t-wiki-1",
                    "hook_event_name": "Stop",
                },
                repo,
            )
            self.assertIn("systemMessage", result)
            self.assertIn("Wiki save proposals", result["systemMessage"])
            # no durable notes auto-written from plain summary alone
            notes = list((repo / ".codex" / "anyone-can-code" / "memory" / "notes").rglob("*.md"))
            self.assertEqual(notes, [])


if __name__ == "__main__":
    unittest.main()
