"""Item 18: plain AI observability receipt."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ai_observability as obs


def test_plain_receipt_from_journal(tmp_path):
    tools = (
        tmp_path
        / ".codex"
        / "anyone-can-code"
        / "state"
        / "tool-usage.jsonl"
    )
    tools.parent.mkdir(parents=True)
    tools.write_text(
        json.dumps(
            {
                "tool_name": "Bash",
                "command_preview": "python -m pytest -q",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = obs.build_plain_receipt(tmp_path)
    assert receipt["count"] == 1
    assert "pytest" in receipt["user_block"]
    assert "What AI did" in receipt["user_block"]
