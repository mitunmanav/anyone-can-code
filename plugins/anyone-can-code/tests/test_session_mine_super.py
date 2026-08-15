"""You-Brain v1: session_mine_super — local rollout mine, no AI."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import session_mine_super as sms  # noqa: E402

FIXTURE = PLUGIN / "tests" / "fixtures" / "you_brain_tiny_rollout.jsonl"


def _sessions_tree(tmp: Path) -> Path:
    """Copy fixture into a fake ~/.codex/sessions-like tree."""
    root = tmp / "sessions" / "2026" / "07" / "15"
    root.mkdir(parents=True)
    dest = root / "rollout-2026-07-15T10-00-00-019f0000-aaaa-bbbb-cccc-ddddeeee0001.jsonl"
    shutil.copy(FIXTURE, dest)
    return tmp / "sessions"


def test_parse_rollout_stream_extracts_model_effort_tokens_tasks():
    fact = sms.parse_rollout_stream(FIXTURE)
    assert fact is not None
    assert fact["session_id"] == "019f0000-aaaa-bbbb-cccc-ddddeeee0001"
    assert fact["model"] == "gpt-5.6-sol"
    assert fact["reasoning_effort"] == "medium"
    assert fact["tokens"]["total_tokens"] == 1280
    assert "bug-fix" in fact["task_signals"]
    assert "feature" in fact["task_signals"]
    assert fact["user_correction_hits"] >= 1
    assert fact["lines_parsed"] >= 5  # corrupt last line skipped


def test_mine_dry_run_writes_l1_l2_preview_not_you_md(tmp_path):
    sessions = _sessions_tree(tmp_path / "codex")
    memory = tmp_path / "user-memory"
    result = sms.mine(
        sessions_roots=[sessions],
        memory_root=memory,
        max_files=10,
        max_mb=10,
        apply=False,
    )
    assert result["ok"] is True
    assert result["token_cost"] == 0
    assert result["applied"] is False
    assert result["applied_path"] is None

    brain = memory / "you-brain"
    assert (brain / "raw" / "facts.jsonl").exists()
    assert (brain / "aggregates" / "summary.json").exists()
    assert (brain / "YOU.preview.md").exists()
    assert not (brain / "YOU.md").exists()

    preview = (brain / "YOU.preview.md").read_text(encoding="utf-8")
    assert "PREVIEW" in preview
    assert "gpt-5.6-sol" in preview
    assert "Native Codex memories" in preview

    facts = sms.load_l1_facts(brain)
    assert len(facts) >= 1
    agg = json.loads((brain / "aggregates" / "summary.json").read_text(encoding="utf-8"))
    assert agg["sessions"] >= 1
    assert agg["top_model"] == "gpt-5.6-sol"


def test_mine_apply_writes_you_md(tmp_path):
    sessions = _sessions_tree(tmp_path / "codex")
    memory = tmp_path / "user-memory"
    result = sms.mine(
        sessions_roots=[sessions],
        memory_root=memory,
        apply=True,
    )
    assert result["applied"] is True
    you = Path(result["applied_path"])
    assert you.exists()
    text = you.read_text(encoding="utf-8")
    assert "APPLIED" in text
    assert "Soft model tips" in text


def test_ingest_index_skips_unchanged(tmp_path):
    sessions = _sessions_tree(tmp_path / "codex")
    memory = tmp_path / "user-memory"
    r1 = sms.mine(sessions_roots=[sessions], memory_root=memory, apply=False)
    assert r1["receipt"]["files_mined"] == 1
    r2 = sms.mine(sessions_roots=[sessions], memory_root=memory, apply=False)
    assert r2["receipt"]["files_skipped"] == 1
    assert r2["receipt"]["files_mined"] == 0
    # force re-mine
    r3 = sms.mine(
        sessions_roots=[sessions], memory_root=memory, apply=False, force=True
    )
    assert r3["receipt"]["files_mined"] == 1


def test_budget_max_files(tmp_path):
    sessions = tmp_path / "sessions" / "2026" / "07" / "15"
    sessions.mkdir(parents=True)
    for i in range(3):
        dest = sessions / f"rollout-2026-07-15T10-0{i}-00-019f0000-aaaa-bbbb-cccc-ddddeeee000{i}.jsonl"
        shutil.copy(FIXTURE, dest)
    memory = tmp_path / "user-memory"
    result = sms.mine(
        sessions_roots=[tmp_path / "sessions"],
        memory_root=memory,
        max_files=2,
    )
    assert result["receipt"]["files_scanned"] == 2


def test_soft_tip_uses_ledger_with_n_and_confidence(tmp_path):
    import model_ledger

    ledger = tmp_path / "model-ledger.jsonl"
    for _ in range(4):
        model_ledger.record_model_result(
            "gpt-5.6", "bug-fix", "success", reasoning="medium", ledger_path=ledger
        )
    agg = {
        "sessions": 4,
        "task_signals": {"bug-fix": 4},
        "model_by_task": {"bug-fix": {"other": 1}},
        "top_model": "other",
        "top_effort": "medium",
    }
    tips = sms.soft_model_tips(agg, ledger_path=ledger, min_n=2)
    assert tips
    tip = next(t for t in tips if t["task_type"] == "bug-fix")
    assert tip["model"] == "gpt-5.6"
    assert tip["n"] >= 4
    assert 0 < tip["confidence"] <= 0.85
    assert tip["soft"] is True


def test_cli_main_json(tmp_path, capsys):
    sessions = _sessions_tree(tmp_path / "codex")
    memory = tmp_path / "user-memory"
    code = sms.main(
        [
            "--sessions-root",
            str(sessions),
            "--memory-root",
            str(memory),
            "--json",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["ok"] is True
    assert data["token_cost"] == 0


def test_corrupt_only_file_does_not_crash(tmp_path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    bad = sessions / "rollout-bad.jsonl"
    bad.write_text("{not json\nalso bad\n", encoding="utf-8")
    memory = tmp_path / "user-memory"
    result = sms.mine(sessions_roots=[sessions], memory_root=memory)
    assert result["ok"] is True
    # no usable codex signals → may mine empty or corrupt count
    assert result["token_cost"] == 0
