import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import guard
import load_session
import save_session
import state


def test_prompt_submit_marks_turn_open(tmp_path):
    guard.mark_turn_open(tmp_path, "please add a contact form to the site")
    wf = state.read_state(tmp_path)
    assert wf["turn_status"] == "open"
    assert "contact form" in wf["open_ask"]


def test_stop_marks_turn_closed(tmp_path):
    guard.mark_turn_open(tmp_path, "build the page")
    save_session.handle_payload({"last_assistant_message": "Done. Next: test it."}, tmp_path)
    wf = state.read_state(tmp_path)
    assert wf["turn_status"] == "closed"


def test_open_turn_injects_crash_resume_line(tmp_path):
    guard.mark_turn_open(tmp_path, "fix the broken login button")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "CRASH RESUME" in ctx
    assert "login button" in ctx


def test_closed_turn_has_no_crash_line(tmp_path):
    guard.mark_turn_open(tmp_path, "fix login")
    save_session.handle_payload({"last_assistant_message": "done"}, tmp_path)
    ctx = load_session.build_context(tmp_path, "startup")
    assert "CRASH RESUME" not in ctx


def test_open_ask_is_scrubbed(tmp_path):
    guard.mark_turn_open(tmp_path, "use api_key: sk-abcdefghijklmnop123456 please")
    wf = state.read_state(tmp_path)
    assert "sk-abcdefghijklmnop123456" not in wf["open_ask"]
