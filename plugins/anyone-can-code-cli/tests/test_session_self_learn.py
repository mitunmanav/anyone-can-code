"""Item 8: free self-learning from local session files (0 tokens)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import session_self_learn as ssl


def _rollout(path: Path, lines: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(x) for x in lines) + "\n",
        encoding="utf-8",
    )


def test_mines_user_correction_and_failure(tmp_path):
    sessions = tmp_path / "sessions" / "2026" / "07" / "15"
    _rollout(
        sessions / "rollout-a.jsonl",
        [
            {
                "type": "event_msg",
                "payload": {
                    "type": "user_message",
                    "message": "Never use npm on Windows, always use npm.cmd",
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Command failed: exit code 1 permission denied",
                },
            },
        ],
    )
    result = ssl.mine_sessions([tmp_path / "sessions"])
    assert result["token_cost"] == 0
    assert result["count"] >= 1
    joined = " ".join(x["summary"].lower() for x in result["lessons"])
    assert "never" in joined or "npm" in joined or "failed" in joined or "permission" in joined


def test_write_lessons_to_project(tmp_path):
    lessons = [
        {"summary": "Always run npm.cmd on Windows", "hits": 3, "kind": "lesson"},
    ]
    out = ssl.write_lessons_to_project(tmp_path, lessons)
    assert out["written"] == 1
    notes = list((tmp_path / ".codex" / "anyone-can-code" / "memory" / "notes" / "project").glob("*.md"))
    assert len(notes) == 1
    text = notes[0].read_text(encoding="utf-8")
    assert "npm.cmd" in text
    assert 'kind: "lesson"' in text
    # rerun safe
    out2 = ssl.write_lessons_to_project(tmp_path, lessons)
    assert out2["written"] == 0
