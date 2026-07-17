import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import load_session
import memory_core
import save_session
import state


def test_stop_writes_now_md(tmp_path):
    state.write_state(tmp_path, {"active_goal": "build waitlist site", "next_step": "add form"})
    save_session.handle_payload({"last_assistant_message": "Form added. We decided to use SQLite."}, tmp_path)
    now = state.ensure_project_layout(tmp_path)["memory"] / "NOW.md"
    text = now.read_text(encoding="utf-8")
    assert "build waitlist site" in text
    assert "Next:" in text


def test_now_md_written_every_stop_even_idle(tmp_path):
    save_session.handle_payload({"last_assistant_message": ""}, tmp_path)
    now = state.ensure_project_layout(tmp_path)["memory"] / "NOW.md"
    assert now.exists()


def test_session_start_writes_heartbeat(tmp_path):
    load_session.handle_payload({"source": "startup"}, tmp_path)
    mem = state.ensure_project_layout(tmp_path)["memory"]
    assert memory_core.heartbeat_age_seconds(mem) is not None


def test_memory_block_is_capped(tmp_path):
    state.write_state(tmp_path, {"active_goal": "g" * 500, "next_step": "n" * 500,
                                 "last_decision": "d" * 500})
    block = load_session.build_memory_block(tmp_path, "startup")
    assert len(block) <= 1500
    assert block.startswith("NOW:")
