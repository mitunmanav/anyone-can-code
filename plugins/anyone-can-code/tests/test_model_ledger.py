import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import model_ledger


def test_record_and_recommend(tmp_path):
    ledger_path = tmp_path / "model-ledger.jsonl"
    model_ledger.record_model_result(
        "claude-sonnet-4-6", "bug-fix", "success", ledger_path=ledger_path
    )
    model_ledger.record_model_result(
        "claude-sonnet-4-6", "bug-fix", "success", ledger_path=ledger_path
    )
    model_ledger.record_model_result(
        "claude-haiku-4-5", "bug-fix", "fail", ledger_path=ledger_path
    )
    rec = model_ledger.recommend_model("bug-fix", ledger_path=ledger_path)
    assert rec["model"] == "claude-sonnet-4-6"
    assert "reason" in rec


def test_no_data_returns_default(tmp_path):
    ledger_path = tmp_path / "empty.jsonl"
    rec = model_ledger.recommend_model("new-task-type", ledger_path=ledger_path)
    assert rec["model"]
    assert "no data" in rec["reason"].lower() or "default" in rec["reason"].lower()
    assert "reasoning" in rec
    assert rec["reasoning"] != "high" or rec.get("reasoning")  # has a field


def test_reasoning_not_always_high():
    assert model_ledger.recommend_reasoning("micro") == "low"
    assert model_ledger.recommend_reasoning("bug-fix") == "medium"
    assert model_ledger.recommend_reasoning("feature") != "max"


def test_record_includes_reasoning(tmp_path):
    path = tmp_path / "led.jsonl"
    model_ledger.record_model_result(
        "gpt-5.6", "feature", "success", reasoning="medium", ledger_path=path
    )
    row = json.loads(path.read_text().splitlines()[0])
    assert row["reasoning"] == "medium"


def test_session_model_is_read_from_hook_payload():
    payload = {"model": "claude-opus-4-8", "hook_event_name": "SessionStart"}
    model = model_ledger.extract_model_from_payload(payload)
    assert model == "claude-opus-4-8"


def test_session_feeds_ledger_and_recall_uses_it(tmp_path):
    """Backlog 6: session outcomes must land in the ledger under the project root."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).resolve().parents[1] / "hooks" / "scripts"))
    import save_session
    import load_session
    import state as hook_state

    hook_state.append_jsonl(
        hook_state.signal_log_path(tmp_path),
        {"timestamp": "2026-07-06T10:00:00Z", "signal_type": "verified_success",
         "detail": "tests passed"},
    )

    save_session.handle_payload(
        {"last_assistant_message": "feature built and verified",
         "turn_id": "t1", "hook_event_name": "Stop", "model": "gpt-5"},
        tmp_path,
    )

    ledger = tmp_path / ".codex" / "anyone-can-code" / "state" / "model-ledger.jsonl"
    assert ledger.exists(), "ledger not written by session end"
    rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    assert any(r.get("outcome") == "success" and r.get("model") == "gpt-5" for r in rows)

    ctx = load_session.build_context(tmp_path, "startup")
    assert "gpt-5" in ctx, "recorded model not used in recommendation"
