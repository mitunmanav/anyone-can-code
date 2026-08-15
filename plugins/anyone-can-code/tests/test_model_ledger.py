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


def test_classify_task_type_from_keywords():
    assert model_ledger.classify_task_type(text="fix the null pointer crash") == "bug-fix"
    assert model_ledger.classify_task_type(text="rename a typo in one line") == "micro"
    assert model_ledger.classify_task_type(text="research how does hooks work") == "research"
    assert model_ledger.classify_task_type(text="implement a new feature endpoint") == "feature"
    assert model_ledger.classify_task_type(text="run pytest and verify suite") == "verify"
    assert model_ledger.classify_task_type(text="write a plan and architecture") == "plan"
    assert model_ledger.classify_task_type(text="") == "general"


def test_classify_task_type_from_skills_and_tools():
    assert model_ledger.classify_task_type(skills=["systematic-debugging"]) == "bug-fix"
    assert model_ledger.classify_task_type(skills=["writing-plans"]) == "plan"
    assert model_ledger.classify_task_type(skills=["verify"]) == "verify"
    assert model_ledger.classify_task_type(tools=["WebSearch"]) == "research"
    assert model_ledger.classify_task_type(tools=["apply_patch"]) == "feature"


def test_classify_task_type_route_and_signals():
    assert model_ledger.classify_task_type(route="bug-fix") == "bug-fix"
    assert model_ledger.classify_task_type(route="feature-request") == "feature"
    assert (
        model_ledger.classify_task_type(
            signals=[{"signal_type": "note", "detail": "failing test stack trace"}]
        )
        == "bug-fix"
    )
    assert (
        model_ledger.classify_task_type(
            signals=[{"tool_name": "WebSearch", "detail": "looked up docs"}]
        )
        == "research"
    )


def test_recommend_filters_by_task_type(tmp_path):
    """Multi-type ledger: recommend must not bleed scores across task types."""
    path = tmp_path / "multi.jsonl"
    model_ledger.record_model_result("model-a", "bug-fix", "success", ledger_path=path)
    model_ledger.record_model_result("model-a", "bug-fix", "success", ledger_path=path)
    model_ledger.record_model_result("model-b", "feature", "success", ledger_path=path)
    model_ledger.record_model_result("model-b", "feature", "success", ledger_path=path)
    model_ledger.record_model_result("model-a", "feature", "fail", ledger_path=path)
    model_ledger.record_model_result("model-c", "research", "success", ledger_path=path)

    assert model_ledger.recommend_model("bug-fix", ledger_path=path)["model"] == "model-a"
    assert model_ledger.recommend_model("feature", ledger_path=path)["model"] == "model-b"
    assert model_ledger.recommend_model("research", ledger_path=path)["model"] == "model-c"
    # alias route still filters
    assert model_ledger.recommend_model("feature-request", ledger_path=path)["model"] == "model-b"
    # empty type stays isolated
    empty = model_ledger.recommend_model("plan", ledger_path=path)
    assert empty["model"] == model_ledger.DEFAULT_MODEL
    assert "no data" in empty["reason"].lower()


def test_recommend_reasoning_uses_real_task_type():
    assert model_ledger.recommend_reasoning("research") == "high"
    assert model_ledger.recommend_reasoning("micro") == "low"
    assert model_ledger.recommend_reasoning("feature-request") == "medium"
    rec = model_ledger.recommend_model("micro")
    assert rec["reasoning"] == "low"


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
    # Must NOT stick task_type=general when keywords say feature
    feature_rows = [r for r in rows if r.get("model") == "gpt-5" and r.get("outcome") == "success"]
    assert feature_rows
    assert feature_rows[0].get("task_type") != "general"
    assert feature_rows[0].get("task_type") in {"feature", "verify"}

    ctx = load_session.build_context(tmp_path, "startup")
    assert "gpt-5" in ctx, "recorded model not used in recommendation"


def test_task_type_not_stuck_general_on_bug_session(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
    import save_session
    import state as hook_state

    hook_state.append_jsonl(
        hook_state.signal_log_path(tmp_path),
        {"timestamp": "2026-07-06T10:00:00Z", "signal_type": "verified_failure",
         "detail": "stack trace in auth"},
    )
    hook_state.write_state(tmp_path, {"route": "bug-fix", "last_task": "fix login crash"})

    save_session.record_session_model_outcome(
        tmp_path,
        {"model": "gpt-5.6", "last_assistant_message": "still debugging the crash",
         "model_reasoning_effort": "medium"},
        hook_state.read_recent_jsonl(hook_state.signal_log_path(tmp_path), limit=12),
    )
    ledger = tmp_path / ".codex" / "anyone-can-code" / "state" / "model-ledger.jsonl"
    rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    assert rows
    assert rows[0]["task_type"] == "bug-fix"
    assert rows[0]["outcome"] == "fail"
    assert rows[0]["reasoning"] == "medium"
