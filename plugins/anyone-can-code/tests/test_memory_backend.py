from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_memory_server():
    path = PLUGIN_ROOT / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("acc_memory_server", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


server = load_memory_server()


class MemoryBackendTests(unittest.TestCase):
    def test_store_feedback_writes_readable_markdown_and_retrieves_top_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                for index in range(8):
                    server.store_feedback(
                        {
                            "scope": "project",
                            "kind": "pattern",
                            "summary": f"Use Markdown memory for lesson {index}",
                            "confidence": 0.5,
                            "source": "test",
                            "project_root": "C:/project-one",
                        }
                    )

                note_files = list((Path(tmp) / "notes" / "project").glob("*.md"))
                result = server.retrieve_context(
                    {"query": "Markdown memory lesson", "project_root": "C:/project-one", "limit": 99}
                )
                first_note_text = note_files[0].read_text(encoding="utf-8")
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(len(note_files), 8)
        self.assertTrue(first_note_text.startswith("---\n"))
        self.assertEqual(result["mode"], "portable-markdown")
        self.assertLessEqual(result["count"], 5)

    def test_plain_reader_can_follow_markdown_links_without_acc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                stored = server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "decision",
                        "summary": "Keep founder memory portable",
                        "source": "test",
                        "project_root": "C:/portable-project",
                        "related": ["[[decisions/founder-memory]]", "README.md"],
                    }
                )
                text = Path(stored["path"]).read_text(encoding="utf-8")
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertIn("# Keep founder memory portable", text)
        self.assertIn("[[decisions/founder-memory]]", text)
        self.assertIn("README.md", text)

    def test_duplicate_memory_reinforces_existing_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                first = server.store_feedback(
                    {"scope": "user", "kind": "preference", "summary": "Keep replies short", "source": "test"}
                )
                second = server.store_feedback(
                    {"scope": "user", "kind": "preference", "summary": "Keep replies short", "source": "test"}
                )
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(first["record"]["id"], second["record"]["id"])
        self.assertEqual(second["record"]["reinforcement_count"], 2)

    def test_project_scope_does_not_leak_between_projects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "pattern",
                        "summary": "Project alpha private lesson",
                        "source": "test",
                        "project_root": "C:/alpha",
                    }
                )
                alpha = server.retrieve_context({"query": "alpha private lesson", "project_root": "C:/alpha"})
                beta = server.retrieve_context({"query": "alpha private lesson", "project_root": "C:/beta"})
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(alpha["count"], 1)
        self.assertEqual(beta["count"], 0)

    def test_memory_is_advisory_scoped_and_revocable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                stored = server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "pattern",
                        "summary": "Use advisory lesson only when relevant",
                        "source": "test",
                        "project_root": "C:/project-one",
                    }
                )
                before = server.retrieve_context(
                    {"query": "advisory lesson", "project_root": "C:/project-one"}
                )
                revoked = server.revoke_memory({"id": stored["record"]["id"]})
                after = server.retrieve_context(
                    {"query": "advisory lesson", "project_root": "C:/project-one"}
                )
                note_text = Path(stored["path"]).read_text(encoding="utf-8")
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(before["count"], 1)
        self.assertEqual(revoked["record"]["status"], "revoked")
        self.assertEqual(after["count"], 0)
        self.assertIn('status: "revoked"', note_text)

    def test_rebuild_index_is_disposable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                server.store_feedback(
                    {"scope": "shared", "kind": "pattern", "summary": "Shared Markdown lesson", "source": "test"}
                )
                index_path = Path(tmp) / "index" / "memory-index.json"
                index_path.unlink()
                rebuilt = server.rebuild_index({})
                payload = json.loads(index_path.read_text(encoding="utf-8"))
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertTrue(rebuilt["rebuilt"])
        self.assertEqual(payload["count"], 1)

    def test_import_session_files_requires_selected_paths_and_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "session.jsonl"
            source.write_text(json.dumps({"summary": "Verified import lesson"}) + "\n", encoding="utf-8")
            try:
                receipt = server.import_session_files(
                    {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one"}
                )
                receipt_path_exists = Path(receipt["receipt_path"]).exists()
                imported_note = server.parse_markdown_note(Path(receipt["imported"][0]["path"]))
                dry_run = server.import_session_files(
                    {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one", "dry_run": True}
                )
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(receipt["imported_count"], 1)
        self.assertTrue(receipt_path_exists)
        self.assertEqual(imported_note["scope"], "project")
        self.assertEqual(imported_note["provenance"], str(source))
        self.assertEqual(imported_note["source_receipt"], receipt["receipt_id"])
        self.assertEqual(dry_run["imported_count"], 1)
        self.assertNotIn("receipt_path", dry_run)

    def test_session_import_snapshots_before_write_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "session.jsonl"
            source.write_text(json.dumps({"summary": "Stable imported lesson"}) + "\n", encoding="utf-8")
            try:
                first = server.import_session_files(
                    {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one"}
                )
                second = server.import_session_files(
                    {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one"}
                )
                notes = list((Path(tmp) / "memory" / "notes" / "project").glob("*.md"))
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(first["status"], "verified")
        self.assertEqual(first["imported_count"], 1)
        self.assertEqual(len(first["snapshots"]), 1)
        self.assertEqual(second["status"], "verified")
        self.assertEqual(second["imported_count"], 0)
        self.assertEqual(second["skipped_count"], 1)
        self.assertEqual(len(notes), 1)

    def test_failed_session_snapshot_writes_rollback_receipt_and_keeps_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "session.jsonl"
            source.write_text(json.dumps({"summary": "Never partially import me"}) + "\n", encoding="utf-8")
            try:
                with mock.patch.object(server.shutil, "copy2", side_effect=OSError("snapshot failed")):
                    receipt = server.import_session_files(
                        {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one"}
                    )
                source_exists = source.exists()
                rollback_exists = Path(receipt["rollback_receipt_path"]).exists()
                notes = list((Path(tmp) / "memory" / "notes" / "project").glob("*.md"))
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(receipt["status"], "rolled_back")
        self.assertEqual(receipt["imported_count"], 0)
        self.assertTrue(source_exists)
        self.assertTrue(rollback_exists)
        self.assertEqual(notes, [])

    def test_failed_markdown_write_restores_pre_import_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "session.jsonl"
            source.write_text(
                "\n".join(
                    [
                        json.dumps({"summary": "First new lesson"}),
                        json.dumps({"summary": "Second new lesson"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            try:
                existing = server.store_feedback(
                    {"scope": "project", "kind": "pattern", "summary": "Existing lesson", "project_root": "C:/one"}
                )
                existing_text = Path(existing["path"]).read_text(encoding="utf-8")
                real_write_note = server.write_note
                calls = 0

                def fail_second_write(record):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise OSError("write failed")
                    return real_write_note(record)

                with mock.patch.object(server, "write_note", side_effect=fail_second_write):
                    receipt = server.import_session_files(
                        {"paths": [str(source)], "scope": "project", "project_root": "C:/one"}
                    )
                source_exists = source.exists()
                notes = list((Path(tmp) / "memory" / "notes" / "project").glob("*.md"))
                restored_text = Path(existing["path"]).read_text(encoding="utf-8")
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(receipt["status"], "rolled_back")
        self.assertTrue(source_exists)
        self.assertEqual(len(notes), 1)
        self.assertEqual(restored_text, existing_text)

    def test_legacy_jsonl_migration_backs_up_source_and_keeps_it_after_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "legacy-memory.jsonl"
            source.write_text(json.dumps({"summary": "Legacy verified lesson"}) + "\n", encoding="utf-8")
            try:
                receipt = server.migrate_legacy_jsonl(
                    {"paths": [str(source)], "scope": "project", "project_root": "C:/project-one"}
                )
                backup_exists = Path(receipt["backups"][0]).exists()
                source_exists = source.exists()
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["imported_count"], 1)
        self.assertTrue(backup_exists)
        self.assertTrue(source_exists)

    def test_legacy_migration_permission_denial_keeps_source_and_existing_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = str(Path(tmp) / "memory")
            source = Path(tmp) / "legacy-memory.jsonl"
            source.write_text(json.dumps({"summary": "Permission protected lesson"}) + "\n", encoding="utf-8")
            try:
                existing = server.store_feedback(
                    {"scope": "project", "kind": "pattern", "summary": "Existing safe lesson", "project_root": "C:/one"}
                )
                existing_text = Path(existing["path"]).read_text(encoding="utf-8")
                with mock.patch.object(server.shutil, "copy2", side_effect=PermissionError("access denied")):
                    receipt = server.migrate_legacy_jsonl(
                        {"paths": [str(source)], "scope": "project", "project_root": "C:/one"}
                    )
                source_exists = source.exists()
                existing_after = Path(existing["path"]).read_text(encoding="utf-8")
                rollback_exists = Path(receipt["rollback_receipt_path"]).exists()
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertEqual(receipt["status"], "rolled_back")
        self.assertIn("access denied", receipt["error"])
        self.assertTrue(rollback_exists)
        self.assertTrue(source_exists)
        self.assertEqual(existing_after, existing_text)

    def test_secrets_are_redacted_before_markdown_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = os.environ.get("ACC_MCP_DATA_ROOT")
            os.environ["ACC_MCP_DATA_ROOT"] = tmp
            try:
                result = server.store_feedback(
                    {
                        "scope": "project",
                        "kind": "mistake",
                        "summary": "Never save api_key=abcdef1234567890 in memory",
                        "source": "test",
                        "project_root": "C:/one",
                    }
                )
                text = Path(result["path"]).read_text(encoding="utf-8")
            finally:
                if old_root is None:
                    os.environ.pop("ACC_MCP_DATA_ROOT", None)
                else:
                    os.environ["ACC_MCP_DATA_ROOT"] = old_root

        self.assertIn("[REDACTED]", text)
        self.assertNotIn("abcdef1234567890", text)


if __name__ == "__main__":
    unittest.main()


def test_project_scope_requires_project_root():
    """Honesty: project notes must not land in the silent global fallback."""
    import importlib
    import sys
    from pathlib import Path

    mcp = Path(__file__).resolve().parents[1] / "mcp"
    sys.path.insert(0, str(mcp))
    server = importlib.import_module("server")
    try:
        server.normalize_record(
            {"scope": "project", "kind": "decision", "summary": "Use SQLite"}
        )
        raise AssertionError("expected ValueError without project_root")
    except ValueError as exc:
        assert "project_root required" in str(exc)
