"""Safety items 10 + 11: rate-limit 70/90 warn + token-burn warning from session files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import rate_limit_guard as rlg


def _write_rollout(path: Path, used: float, session_total: int = 1000, last_fresh: int = 100) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    last_input = last_fresh + 50
    entry = {
        "timestamp": "2026-07-12T08:00:00Z",
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "total_token_usage": {
                    "input_tokens": session_total,
                    "cached_input_tokens": 0,
                    "output_tokens": 10,
                    "total_tokens": session_total,
                },
                "last_token_usage": {
                    "input_tokens": last_input,
                    "cached_input_tokens": 50,
                    "output_tokens": 5,
                    "total_tokens": last_input + 5,
                },
                "model_context_window": 353400,
            },
            "rate_limits": {
                "primary": {"used_percent": used, "window_minutes": 300},
                "secondary": {"used_percent": 10.0, "window_minutes": 10080},
                "plan_type": "plus",
            },
        },
    }
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")


def test_assess_rate_limit_thresholds():
    ok = rlg.assess_rate_limit(50)
    assert ok["level"] == "ok"
    assert not ok["warn_70"]
    assert ok["user_line"] == ""

    warn = rlg.assess_rate_limit(70)
    assert warn["level"] == "warn"
    assert warn["warn_70"] is True
    assert warn["hard_90"] is False
    assert "70" in warn["user_line"] or "high" in warn["user_line"].lower()

    hard = rlg.assess_rate_limit(90)
    assert hard["level"] == "hard"
    assert hard["hard_90"] is True
    assert "stop" in hard["user_line"].lower() or "full" in hard["user_line"].lower()


def test_assess_token_burn_thresholds():
    quiet = rlg.assess_token_burn(session_total_tokens=1000, last_fresh_input_tokens=100)
    assert quiet["burning"] is False
    assert quiet["user_line"] == ""

    hot = rlg.assess_token_burn(
        session_total_tokens=rlg.TOKEN_BURN_SESSION_TOTAL,
        last_fresh_input_tokens=10,
    )
    assert hot["burning"] is True
    assert "token" in hot["user_line"].lower()


def test_read_latest_snapshot_from_rollout(tmp_path):
    sessions = tmp_path / "sessions" / "2026" / "07" / "12"
    _write_rollout(sessions / "rollout-test.jsonl", used=91.0, session_total=50_000)
    snap = rlg.read_latest_snapshot([tmp_path / "sessions"])
    assert snap["primary_used_percent"] == 91.0
    lines = rlg.build_guard_lines(snap)
    assert any("RATE LIMIT" in line for line in lines)


def test_build_guard_lines_quiet_when_low(tmp_path):
    sessions = tmp_path / "sessions"
    _write_rollout(sessions / "rollout-low.jsonl", used=5.0)
    lines = rlg.build_guard_lines(rlg.read_latest_snapshot([sessions]))
    assert lines == []
