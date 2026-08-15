"""bite_plan: 2–5 min checkbox steps → artifacts/BITE_PLAN.md."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import bite_plan  # noqa: E402


def test_path_under_artifacts(tmp_path: Path) -> None:
    path = bite_plan.bite_plan_path(tmp_path)
    assert path == tmp_path / ".codex" / "anyone-can-code" / "artifacts" / "BITE_PLAN.md"


def test_clamp_minutes_range() -> None:
    assert bite_plan.clamp_minutes(1) == 2
    assert bite_plan.clamp_minutes(2) == 2
    assert bite_plan.clamp_minutes(5) == 5
    assert bite_plan.clamp_minutes(9) == 5
    assert bite_plan.clamp_minutes(None) == bite_plan.DEFAULT_MINUTES
    assert bite_plan.clamp_minutes("3") == 3


def test_normalize_step_strips_checkbox_and_sets_minutes() -> None:
    step = bite_plan.normalize_step("- [x] Write failing test")
    assert step["done"] is True
    assert step["text"] == "Write failing test"
    assert 2 <= step["minutes"] <= 5

    step2 = bite_plan.normalize_step({"text": "Run tests", "minutes": 10, "done": False})
    assert step2["minutes"] == 5
    assert step2["done"] is False
    assert step2["text"] == "Run tests"


def test_build_markdown_has_checkboxes_and_time() -> None:
    md = bite_plan.build_markdown(
        goal="Add login",
        steps=["Write failing test", "Implement minimal login", "Run pytest"],
        architecture="Session cookie auth",
    )
    assert "# Bite plan:" in md
    assert "**Goal:** Add login" in md
    assert "Session cookie auth" in md
    assert "- [ ]" in md
    assert "~" in md and "min" in md
    assert "Write failing test" in md
    assert "2–5" in md or "2-5" in md


def test_write_and_assess_ok(tmp_path: Path) -> None:
    path = bite_plan.write_bite_plan(
        tmp_path,
        goal="Ship auth",
        steps=[
            "Write failing test for login",
            "Implement login handler",
            "Run pytest login file",
        ],
    )
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "- [ ]" in text
    assert "Ship auth" in text

    result = bite_plan.assess_bite_plan(tmp_path)
    assert result["status"] == "ok"
    assert result["step_count"] == 3
    assert result["open_count"] == 3
    assert result["done_count"] == 0
    assert result["exists"] is True
    assert result["path"].endswith("BITE_PLAN.md")


def test_assess_missing_empty_no_steps(tmp_path: Path) -> None:
    missing = bite_plan.assess_bite_plan(tmp_path)
    assert missing["status"] == "missing"

    path = bite_plan.bite_plan_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("   \n", encoding="utf-8")
    assert bite_plan.assess_bite_plan(tmp_path)["status"] == "empty"

    path.write_text("# Bite plan\n\nJust prose, no checkboxes.\n", encoding="utf-8")
    assert bite_plan.assess_bite_plan(tmp_path)["status"] == "no_steps"


def test_parse_steps_from_markdown() -> None:
    text = """
# Bite plan: demo

- [ ] **1.** First step `(~3 min)`
- [x] **2.** Second step `(~2 min)`
- [ ] plain step
"""
    steps = bite_plan.parse_steps(text)
    assert len(steps) == 3
    assert steps[0]["done"] is False
    assert steps[1]["done"] is True
    assert "First step" in steps[0]["text"]
    assert steps[0]["minutes"] == 3


def test_mark_step_done(tmp_path: Path) -> None:
    bite_plan.write_bite_plan(
        tmp_path,
        goal="Demo",
        steps=["Step A", "Step B"],
    )
    bite_plan.mark_step(tmp_path, 1, done=True)
    result = bite_plan.assess_bite_plan(tmp_path)
    assert result["done_count"] == 1
    assert result["open_count"] == 1
    text = bite_plan.bite_plan_path(tmp_path).read_text(encoding="utf-8")
    assert "- [x]" in text
    assert "- [ ]" in text
    # No doubled minute suffixes after mark rewrite
    assert text.count("(~") == text.count("min)")
    for step in result["steps"]:
        assert "(~" not in step["text"]
        assert "min)" not in step["text"]


def test_roundtrip_parse_strips_built_minutes(tmp_path: Path) -> None:
    bite_plan.write_bite_plan(
        tmp_path,
        goal="RT",
        steps=[{"text": "Only action", "minutes": 4}],
    )
    steps = bite_plan.parse_steps(
        bite_plan.bite_plan_path(tmp_path).read_text(encoding="utf-8")
    )
    assert len(steps) == 1
    assert steps[0]["text"] == "Only action"
    assert steps[0]["minutes"] == 4


def test_cli_write_and_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = bite_plan.main(
        [
            "--repo",
            str(tmp_path),
            "--write",
            "--goal",
            "Feature X",
            "--step",
            "Write failing test",
            "--step",
            "Implement minimal code",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"
    assert out["step_count"] == 2
    assert bite_plan.bite_plan_path(tmp_path).is_file()


def test_cli_assess_missing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = bite_plan.main(["--repo", str(tmp_path), "--json"])
    assert code == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "missing"


def test_skill_frontmatter_and_display_name() -> None:
    skill_md = (PLUGIN / "skills" / "bite-plan" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: bite-plan" in skill_md
    assert "BITE_PLAN.md" in skill_md
    assert "2-5" in skill_md or "2–5" in skill_md
    yaml_text = (
        PLUGIN / "skills" / "bite-plan" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert 'display_name: "ACC bite plan"' in yaml_text
    assert "allow_implicit_invocation: false" in yaml_text


def test_skill_under_budget() -> None:
    size = len(
        (PLUGIN / "skills" / "bite-plan" / "SKILL.md").read_text(encoding="utf-8")
    )
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
