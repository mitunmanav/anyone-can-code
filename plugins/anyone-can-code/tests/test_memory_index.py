import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import memory_index
import memory_promote
import state


def _seed(tmp_path):
    memory_promote.write_promote_note(tmp_path, "decision", "use SQLite for the waitlist storage")
    memory_promote.write_promote_note(tmp_path, "want", "always use the blue theme")
    memory_promote.write_promote_note(tmp_path, "correction", "the contact page is contact.html not about.html")
    return state.ensure_project_layout(tmp_path)["memory"]


def test_rebuild_counts_notes(tmp_path):
    mem = _seed(tmp_path)
    result = memory_index.rebuild(mem)
    assert result["count"] == 3
    assert result["backend"] in {"fts5", "like"}


def test_search_finds_relevant_note(tmp_path):
    mem = _seed(tmp_path)
    memory_index.rebuild(mem)
    hits = memory_index.search(mem, "waitlist storage", limit=3)
    assert hits and "SQLite" in hits[0]["summary"]


def test_index_is_disposable(tmp_path):
    mem = _seed(tmp_path)
    memory_index.rebuild(mem)
    (mem / "memory.sqlite").unlink()
    hits = memory_index.search(mem, "blue theme")
    assert hits, "search did not auto-rebuild after index deletion"


def test_corrupt_index_recovers(tmp_path):
    mem = _seed(tmp_path)
    memory_index.rebuild(mem)
    (mem / "memory.sqlite").write_bytes(b"garbage not a database")
    hits = memory_index.search(mem, "contact page")
    assert hits, "search did not recover from corrupt index"


def test_search_never_raises_on_empty(tmp_path):
    mem = state.ensure_project_layout(tmp_path)["memory"]
    assert memory_index.search(mem, "anything") == []
