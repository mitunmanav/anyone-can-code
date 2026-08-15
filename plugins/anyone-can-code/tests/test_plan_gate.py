"""plan_gate: plan artifact must exist with steps before product writes."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import plan_gate  # noqa: E402


def _write_plan(repo: Path, body: str) -> Path:
    path = plan_gate.plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_missing_plan(tmp_path: Path) -> None:
    result = plan_gate.assess_plan(tmp_path)
    assert result["status"] == "missing"
    assert result["can_write_product"] is False
    assert result["path"].endswith("PLAN.md")
    assert "missing" in result["message"].lower() or "no plan" in result["message"].lower()


def test_empty_plan(tmp_path: Path) -> None:
    _write_plan(tmp_path, "   \n")
    result = plan_gate.assess_plan(tmp_path)
    assert result["status"] == "empty"
    assert result["can_write_product"] is False


def test_plan_exists_with_steps(tmp_path: Path) -> None:
    _write_plan(
        tmp_path,
        "# Plan\n\n- Add login form\n- Wire API\n- Verify with tests\n",
    )
    result = plan_gate.assess_plan(tmp_path)
    assert result["status"] == "ok"
    assert result["can_write_product"] is True
    assert result["step_count"] >= 3
    assert result["exists"] is True


def test_plan_no_steps(tmp_path: Path) -> None:
    _write_plan(tmp_path, "# Plan\n\nJust a paragraph with no list steps.\n")
    result = plan_gate.assess_plan(tmp_path)
    assert result["status"] == "no_steps"
    assert result["can_write_product"] is False
    assert result["step_count"] == 0


def test_stale_plan(tmp_path: Path) -> None:
    path = _write_plan(
        tmp_path,
        "# Plan\n\n1. Old step one\n2. Old step two\n",
    )
    # File age > 48h relative to fixed now
    old = time.time() - (50 * 3600)
    os.utime(path, (old, old))
    now = time.time()
    result = plan_gate.assess_plan(tmp_path, now=now, max_age_hours=48)
    assert result["status"] == "stale"
    assert result["can_write_product"] is False
    assert result["age_hours"] is not None
    assert result["age_hours"] >= 48


def test_fresh_plan_not_stale(tmp_path: Path) -> None:
    path = _write_plan(
        tmp_path,
        "# Plan\n\n1. Step A\n2. Step B\n",
    )
    now = time.time()
    os.utime(path, (now - 3600, now - 3600))
    result = plan_gate.assess_plan(tmp_path, now=now, max_age_hours=48)
    assert result["status"] == "ok"
    assert result["can_write_product"] is True


def test_extract_steps_numbered_and_bullets() -> None:
    text = """
    Goal: ship auth
    1. Create user model
    2. Add login route
    - Write tests
    * Deploy checklist
    """
    steps = plan_gate.extract_steps(text)
    assert len(steps) >= 4


def test_is_product_write_apply_patch() -> None:
    assert plan_gate.is_product_write(
        "apply_patch",
        {"command": "*** Update File: src/app.py\n@@\n-a\n+b\n"},
    )
    assert not plan_gate.is_product_write(
        "apply_patch",
        {
            "command": (
                "*** Update File: .codex/anyone-can-code/artifacts/PLAN.md\n"
                "@@\n-old\n+new\n"
            )
        },
    )
    assert not plan_gate.is_product_write("Bash", {"command": "ls"})


def test_pretool_soft_hint_when_required_and_missing(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"command": "*** Update File: src/main.py\n@@\n+x\n"},
    }
    hint = plan_gate.pretool_soft_hint(
        tmp_path,
        payload,
        prefs={"plan_gate_required": True},
    )
    assert hint
    assert "plan" in hint.lower()
    assert "PLAN.md" in hint or "plan-gate" in hint.lower() or "$plan" in hint


def test_pretool_soft_hint_off_by_default(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"command": "*** Update File: src/main.py\n@@\n+x\n"},
    }
    assert plan_gate.pretool_soft_hint(tmp_path, payload, prefs={}) is None
    assert plan_gate.pretool_soft_hint(tmp_path, payload, prefs=None) is None


def test_pretool_soft_hint_skipped_when_plan_ok(tmp_path: Path) -> None:
    _write_plan(tmp_path, "# Plan\n\n- Step one\n- Step two\n")
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"command": "*** Update File: src/main.py\n@@\n+x\n"},
    }
    assert (
        plan_gate.pretool_soft_hint(
            tmp_path,
            payload,
            prefs={"plan_gate_required": True},
        )
        is None
    )


def test_write_plan_skeleton(tmp_path: Path) -> None:
    path = plan_gate.write_plan_skeleton(
        tmp_path,
        goal="Add dark mode",
        steps=["Theme tokens", "Toggle UI", "Verify contrast"],
    )
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "dark mode" in body.lower()
    assert plan_gate.assess_plan(tmp_path)["status"] == "ok"
