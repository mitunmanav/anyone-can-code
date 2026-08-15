"""State machine + skill registration for $oneshot (strong one-shot run)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import oneshot_checklist as oc  # noqa: E402


def test_phases_order() -> None:
    assert oc.PHASES == ("plan", "build", "verify", "done")


def test_init_starts_at_plan(tmp_path: Path) -> None:
    state = oc.init_run(tmp_path, goal="ship login")
    assert state["phase"] == "plan"
    assert state["goal"] == "ship login"
    assert state["completed"] == []
    assert state["evidence"] == {}
    assert state["ok_to_claim_done"] is False
    path = oc.state_path(tmp_path)
    assert path.is_file()
    disk = json.loads(path.read_text(encoding="utf-8"))
    assert disk["phase"] == "plan"


def test_happy_path_plan_build_verify_done(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="feature x")
    s1 = oc.advance(tmp_path, "plan", note="PLAN.md written")
    assert s1["phase"] == "build"
    assert "plan" in s1["completed"]

    s2 = oc.advance(tmp_path, "build", note="TDD implement")
    assert s2["phase"] == "verify"
    assert s2["completed"] == ["plan", "build"]

    s3 = oc.advance(
        tmp_path,
        "verify",
        evidence="pytest plugins/anyone-can-code/tests/test_oneshot_checklist.py -q → 8 passed",
    )
    assert s3["phase"] == "done"
    assert s3["ok_to_claim_done"] is True
    assert "verify" in s3["evidence"]
    assert s3["evidence"]["verify"].startswith("pytest")

    s4 = oc.advance(tmp_path, "done")
    assert s4["phase"] == "done"
    assert s4["completed"] == ["plan", "build", "verify", "done"]
    assert s4["ok_to_claim_done"] is True


def test_skip_build_fails(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="x")
    with pytest.raises(oc.OneshotError, match="skip|expected plan"):
        oc.advance(tmp_path, "build")


def test_skip_verify_fails(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="x")
    oc.advance(tmp_path, "plan")
    with pytest.raises(oc.OneshotError, match="skip|expected build"):
        oc.advance(tmp_path, "verify", evidence="pytest -q")


def test_skip_to_done_fails(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="x")
    with pytest.raises(oc.OneshotError, match="skip|expected plan"):
        oc.advance(tmp_path, "done")


def test_verify_requires_evidence(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="x")
    oc.advance(tmp_path, "plan")
    oc.advance(tmp_path, "build")
    with pytest.raises(oc.OneshotError, match="evidence"):
        oc.advance(tmp_path, "verify", evidence="")
    with pytest.raises(oc.OneshotError, match="evidence"):
        oc.advance(tmp_path, "verify")


def test_cannot_claim_done_without_verify_evidence(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="x")
    oc.advance(tmp_path, "plan")
    oc.advance(tmp_path, "build")
    status = oc.status(tmp_path)
    assert status["ok_to_claim_done"] is False
    with pytest.raises(oc.OneshotError, match="verify|evidence|done"):
        oc.assert_can_claim_done(tmp_path)


def test_status_card_shape(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="one focused goal")
    oc.advance(tmp_path, "plan", note="steps in PLAN.md")
    card = oc.status_card(tmp_path)
    assert "WHERE:" in card
    assert "PHASE:" in card
    assert "plan" in card.lower() or "build" in card.lower()
    assert "DONE?" in card or "ok_to_claim_done" in card.lower() or "NO" in card


def test_optional_ledger_write_when_requested(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="ledger goal")
    path = oc.touch_ledger(
        tmp_path,
        where="oneshot: ledger goal",
        next_step="write PLAN.md",
    )
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "WHERE" in text
    assert "ledger goal" in text
    assert "NEXT" in text


def test_cli_status_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    oc.init_run(tmp_path, goal="cli goal")
    code = oc.main(["--repo", str(tmp_path), "status", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["phase"] == "plan"
    assert data["goal"] == "cli goal"


def test_cli_advance_skip_exits_nonzero(tmp_path: Path) -> None:
    oc.init_run(tmp_path, goal="cli")
    code = oc.main(["--repo", str(tmp_path), "advance", "verify", "--evidence", "x"])
    assert code != 0


def test_skill_frontmatter_and_display_name() -> None:
    skill_md = (PLUGIN / "skills" / "oneshot" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: oneshot" in skill_md
    assert "PLAN.md" in skill_md or "plan" in skill_md.lower()
    assert "verify" in skill_md.lower()
    assert "done" in skill_md.lower()
    yaml_text = (PLUGIN / "skills" / "oneshot" / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    assert 'display_name: "ACC strong run"' in yaml_text
    assert "allow_implicit_invocation: false" in yaml_text


def test_skill_under_budget() -> None:
    size = len((PLUGIN / "skills" / "oneshot" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
