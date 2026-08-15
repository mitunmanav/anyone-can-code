"""Tool-call budget (Cascade-style soft limit): session counter + soft warn."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import tool_budget as tb  # noqa: E402


def test_default_limit_matches_cascade_twenty():
    assert tb.DEFAULT_LIMIT == 20


def test_assess_ok_soft_over():
    ok = tb.assess(0, 20)
    assert ok["level"] == "ok"
    assert ok["over"] is False
    assert ok["warn_line"] == ""

    soft = tb.assess(16, 20)  # 80%
    assert soft["level"] == "soft"
    assert soft["over"] is False
    assert "soft" in soft["warn_line"].lower() or "budget" in soft["warn_line"].lower()

    over = tb.assess(20, 20)
    assert over["level"] == "over"
    assert over["over"] is True
    assert "budget" in over["warn_line"].lower()
    # soft only — never hard deny wording as the only message
    assert "deny" not in over["warn_line"].lower()


def test_init_increment_status_continue(tmp_path: Path):
    path = tb.init(tmp_path, limit=5)
    assert path.is_file()
    assert path.name == "tool-budget.json"

    st = tb.status(tmp_path)
    assert st["count"] == 0
    assert st["limit"] == 5
    assert st["remaining"] == 5
    assert st["level"] == "ok"

    for _ in range(4):
        tb.increment(tmp_path, tool_name="Bash")
    st = tb.status(tmp_path)
    assert st["count"] == 4
    assert st["level"] == "soft"  # 4/5 = 80%

    tb.increment(tmp_path, tool_name="apply_patch")
    st = tb.status(tmp_path)
    assert st["count"] == 5
    assert st["over"] is True
    assert st["level"] == "over"

    # continue = new segment, count resets (Cascade continue button parity)
    tb.continue_segment(tmp_path)
    st = tb.status(tmp_path)
    assert st["count"] == 0
    assert st["segment"] == 2
    assert st["limit"] == 5
    assert st["over"] is False


def test_set_limit_and_reset(tmp_path: Path):
    tb.init(tmp_path, limit=10)
    tb.increment(tmp_path)
    tb.increment(tmp_path)
    tb.set_limit(tmp_path, 3)
    st = tb.status(tmp_path)
    assert st["limit"] == 3
    assert st["count"] == 2
    tb.reset(tmp_path)
    st = tb.status(tmp_path)
    assert st["count"] == 0
    assert st["segment"] == 1


def test_is_clean_post_tool():
    assert tb.is_clean_post_tool(
        {"tool_name": "Bash", "tool_response": {"exit_code": 0, "output": "ok"}}
    )
    assert not tb.is_clean_post_tool(
        {"tool_name": "Bash", "tool_response": {"exit_code": 1, "output": "fail"}}
    )
    assert not tb.is_clean_post_tool(
        {"tool_name": "Bash", "tool_response": "Command failed with exit code 2"}
    )
    # unknown exit, no failure tokens → treat clean
    assert tb.is_clean_post_tool(
        {"tool_name": "apply_patch", "tool_response": {"success": True}}
    )


def test_maybe_track_skips_dirty_and_prefs_off(tmp_path: Path):
    tb.init(tmp_path, limit=2)
    # dirty — no increment
    out = tb.maybe_track_post_tool_use(
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_response": {"exit_code": 1},
        },
    )
    assert out == ""
    assert tb.status(tmp_path)["count"] == 0

    # prefs off
    prefs = (
        tmp_path
        / ".codex"
        / "anyone-can-code"
        / "settings"
        / "preferences.json"
    )
    prefs.parent.mkdir(parents=True, exist_ok=True)
    prefs.write_text(json.dumps({"tool_budget_track": False}), encoding="utf-8")
    out = tb.maybe_track_post_tool_use(
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_response": {"exit_code": 0},
        },
    )
    assert out == ""
    assert tb.status(tmp_path)["count"] == 0


def test_maybe_track_clean_increments_and_soft_warns(tmp_path: Path):
    tb.init(tmp_path, limit=10)
    out1 = tb.maybe_track_post_tool_use(
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_response": {"exit_code": 0},
        },
    )
    # 1/10 → ok, no warn
    assert out1 == ""
    assert tb.status(tmp_path)["count"] == 1

    for _ in range(9):
        out2 = tb.maybe_track_post_tool_use(
            tmp_path,
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_response": {"exit_code": 0},
            },
        )
    assert tb.status(tmp_path)["count"] == 10
    assert out2  # over warn
    assert "budget" in out2.lower()


def test_skill_files_exist_and_budget():
    skill_md = PLUGIN / "skills" / "tool-budget" / "SKILL.md"
    yaml_path = PLUGIN / "skills" / "tool-budget" / "agents" / "openai.yaml"
    assert skill_md.is_file()
    assert yaml_path.is_file()
    text = skill_md.read_text(encoding="utf-8")
    assert len(text) <= 4000
    assert "name: tool-budget" in text
    y = yaml_path.read_text(encoding="utf-8")
    assert 'display_name: "ACC tool budget"' in y
    assert "allow_implicit_invocation: false" in y


def test_cli_status_json(tmp_path: Path, capsys):
    tb.init(tmp_path, limit=7)
    rc = tb.main(["--project", str(tmp_path), "--json", "status"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["limit"] == 7
    assert data["count"] == 0
