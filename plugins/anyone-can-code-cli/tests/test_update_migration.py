# plugins/anyone-can-code/tests/test_update_migration.py
"""Beta.4 T4: $update moves taste notes global, re-scopes project facts."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import update as update_mod


def make_note(folder: Path, name: str, kind: str, scope: str, summary: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    folder.joinpath(name).write_text(
        f"---\nid: \"{name[:-3]}\"\nkind: \"{kind}\"\nscope: \"{scope}\"\nstatus: \"active\"\n---\n"
        f"# Note\n\n## Summary\n\n{summary}\n",
        encoding="utf-8",
    )


def test_taste_moves_global_project_fact_rescoped(monkeypatch, tmp_path):
    monkeypatch.setenv("ACC_USER_MEMORY_ROOT", str(tmp_path / "global-user"))
    project = tmp_path / "proj"
    user_notes = project / ".codex" / "anyone-can-code" / "memory" / "notes" / "user"
    make_note(user_notes, "taste-1.md", "preference", "user", "Likes short answers")
    make_note(user_notes, "fact-1.md", "lesson", "user", "This repo uses pnpm")

    result = update_mod.migrate_user_drawer(project)

    assert result["moved"] == 1
    assert result["rescoped"] == 1
    moved = list((tmp_path / "global-user" / "notes" / "user").glob("*.md"))
    assert len(moved) == 1 and "Likes short answers" in moved[0].read_text(encoding="utf-8")
    rescoped = (project / ".codex" / "anyone-can-code" / "memory" / "notes" / "project").glob("*.md")
    assert any("pnpm" in p.read_text(encoding="utf-8") for p in rescoped)
    assert not list(user_notes.glob("*.md")), "old project-local user folder emptied"


def test_migration_is_rerun_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("ACC_USER_MEMORY_ROOT", str(tmp_path / "global-user"))
    project = tmp_path / "proj"
    make_note(project / ".codex" / "anyone-can-code" / "memory" / "notes" / "user",
              "taste-1.md", "preference", "user", "Likes short answers")
    update_mod.migrate_user_drawer(project)
    second = update_mod.migrate_user_drawer(project)
    assert second["moved"] == 0 and second["rescoped"] == 0
    assert len(list((tmp_path / "global-user" / "notes" / "user").glob("*.md"))) == 1
