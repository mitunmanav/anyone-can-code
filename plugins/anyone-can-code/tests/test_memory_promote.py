import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import load_session
import memory_promote
import state


def test_detect_want_from_prompt():
    hits = memory_promote.detect_promotes("please always use the blue theme on every page", "prompt")
    assert any(h["kind"] == "want" for h in hits)


def test_detect_correction_from_prompt():
    hits = memory_promote.detect_promotes("no, that's wrong. I said the CONTACT page, not about.", "prompt")
    assert any(h["kind"] == "correction" for h in hits)


def test_detect_decision_from_stop_text():
    hits = memory_promote.detect_promotes("We decided to go with SQLite for storage. Next: wire it in.", "stop")
    assert any(h["kind"] == "decision" for h in hits)


def test_negative_guard_never_mind():
    assert memory_promote.detect_promotes("never mind, it works now", "prompt") == []


def test_plain_chat_promotes_nothing():
    assert memory_promote.detect_promotes("how does this page look?", "prompt") == []


def test_cap_three_per_call():
    text = ("I want a red header. Never use popups. Always ask before deleting. "
            "I prefer short answers. Remember that I hate modals.")
    assert len(memory_promote.detect_promotes(text, "prompt")) <= 3


def test_write_note_dedup_reinforces(tmp_path):
    first = memory_promote.write_promote_note(tmp_path, "want", "always use the blue theme")
    second = memory_promote.write_promote_note(tmp_path, "want", "always use the blue theme")
    assert first == second
    notes_dir = state.ensure_project_layout(tmp_path)["memory"] / "notes"
    text = (notes_dir / first).read_text(encoding="utf-8")
    assert "reinforcement_count: 2" in text


def test_promoted_note_is_recalled_next_session(tmp_path):
    memory_promote.write_promote_note(tmp_path, "decision", "use SQLite for storage")
    lessons, _proof = load_session.recall_memory_notes(tmp_path)
    assert any("SQLite" in line for line in lessons)


def test_note_excerpt_is_scrubbed(tmp_path):
    name = memory_promote.write_promote_note(tmp_path, "want", "always send token=abcd1234secretxyz99 header")
    notes_dir = state.ensure_project_layout(tmp_path)["memory"] / "notes"
    assert "abcd1234secretxyz99" not in (notes_dir / name).read_text(encoding="utf-8")
