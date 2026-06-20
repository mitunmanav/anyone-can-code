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


def test_session_model_is_read_from_hook_payload():
    payload = {"model": "claude-opus-4-8", "hook_event_name": "SessionStart"}
    model = model_ledger.extract_model_from_payload(payload)
    assert model == "claude-opus-4-8"
