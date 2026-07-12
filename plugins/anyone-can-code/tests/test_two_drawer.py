# plugins/anyone-can-code/tests/test_two_drawer.py
"""Beta.4 T1: user taste notes live in one global drawer; project notes live in the project."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def load_server(monkeypatch, tmp_path):
    monkeypatch.setenv("ACC_USER_MEMORY_ROOT", str(tmp_path / "global-user"))
    monkeypatch.delenv("ACC_MCP_DATA_ROOT", raising=False)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex-home"))
    spec = importlib.util.spec_from_file_location("acc_server_t1", PLUGIN / "mcp" / "server.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_user_note_lands_in_global_drawer(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-a"
    project.mkdir()
    server.store_feedback({
        "scope": "user", "kind": "preference",
        "summary": "User likes short answers",
        "project_root": str(project),
    })
    global_notes = list((tmp_path / "global-user" / "notes" / "user").glob("*.md"))
    assert len(global_notes) == 1
    assert not list(project.rglob("*.md")), "user taste must not land in the project"


def test_project_note_lands_inside_project(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-b"
    project.mkdir()
    server.store_feedback({
        "scope": "project", "kind": "lesson",
        "summary": "This repo uses pnpm not npm",
        "project_root": str(project),
    })
    local_notes = list((project / ".codex" / "anyone-can-code" / "memory" / "notes" / "project").glob("*.md"))
    assert len(local_notes) == 1


def test_retrieve_merges_both_drawers(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-c"
    project.mkdir()
    server.store_feedback({"scope": "user", "kind": "preference",
                           "summary": "User prefers plain words", "project_root": str(project)})
    server.store_feedback({"scope": "project", "kind": "lesson",
                           "summary": "Plain words needed in error pages", "project_root": str(project)})
    result = server.retrieve_context({"query": "plain words", "project_root": str(project)})
    scopes = {item["scope"] for item in result["items"]}
    assert scopes == {"user", "project"}


def test_two_projects_never_mix(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    a, b = tmp_path / "proj-a", tmp_path / "proj-b"
    a.mkdir(); b.mkdir()
    server.store_feedback({"scope": "project", "kind": "lesson",
                           "summary": "Secret feature alpha plan", "project_root": str(a)})
    result = server.retrieve_context({"query": "secret feature alpha", "project_root": str(b)})
    assert all(item["scope"] != "project" for item in result["items"])


def test_revoke_reaches_project_drawer(monkeypatch, tmp_path):
    """Fix round 1: revoke_memory must reach a note stored in a project's own drawer."""
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-revoke"
    project.mkdir()
    stored = server.store_feedback({
        "scope": "project", "kind": "lesson",
        "summary": "Revoke me please",
        "project_root": str(project),
    })
    record_id = stored["record"]["id"]

    result = server.revoke_memory({"id": record_id, "project_root": str(project)})

    assert result["updated"] is True
    assert result["record"]["status"] == "revoked"
    remaining = server.active_rows("project", str(project))
    assert all(row["id"] != record_id for row in remaining)


def test_promote_reaches_project_drawer(monkeypatch, tmp_path):
    """Fix round 1: promote_memory must reach a note stored in a project's own drawer."""
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-promote"
    project.mkdir()
    stored = server.store_feedback({
        "scope": "project", "kind": "lesson",
        "summary": "Promote me please",
        "project_root": str(project),
    })
    record_id = stored["record"]["id"]
    starting_confidence = float(stored["record"]["confidence"])

    result = server.promote_memory({"id": record_id, "project_root": str(project)})

    assert result["promoted"] is True
    assert result["record"]["id"] == record_id
    assert float(result["record"]["confidence"]) > starting_confidence


def test_search_shared_reaches_project_drawer(monkeypatch, tmp_path):
    """Fix round 1: search_shared must reach a shared note stored in a project's own drawer."""
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-shared"
    project.mkdir()
    server.store_feedback({
        "scope": "shared", "kind": "pattern",
        "summary": "Shared onboarding checklist pattern",
        "project_root": str(project),
    })

    result = server.search_shared({"query": "onboarding checklist", "project_root": str(project)})

    assert result["count"] == 1
    assert result["items"][0]["summary"] == "Shared onboarding checklist pattern"


def test_rebuild_index_reaches_project_drawer(monkeypatch, tmp_path):
    """Fix round 1: rebuild_index must count a note stored in a project's own drawer."""
    server = load_server(monkeypatch, tmp_path)
    project = tmp_path / "proj-rebuild"
    project.mkdir()
    server.store_feedback({
        "scope": "project", "kind": "lesson",
        "summary": "Index me please",
        "project_root": str(project),
    })

    result = server.rebuild_index({"project_root": str(project)})

    assert result["count"] >= 1
    import json as _json
    payload = _json.loads(Path(result["path"]).read_text(encoding="utf-8"))
    summaries = [item["summary"] for item in payload["items"]]
    assert "Index me please" in summaries
