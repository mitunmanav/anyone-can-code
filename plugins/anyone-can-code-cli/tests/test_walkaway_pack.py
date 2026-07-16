"""Phase D: walk-away pack wraps native /goal, notify, cloud, review, Sites."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import walkaway_pack as wp


def test_goal_template_has_outcome_constraints_done():
    text = wp.format_goal_prompt("Login page works", "Windows first", "User can sign in")
    assert "Outcome:" in text
    assert "Constraints:" in text
    assert "Done when:" in text
    assert "Login page" in text


def test_walkthrough_plain_lines():
    assert "now" in wp.walkthrough_line("the login page", "start").lower()
    assert "done" in wp.walkthrough_line("the login page", "done").lower()
    assert "stuck" in wp.walkthrough_line("deploy", "fail").lower()
    block = wp.walkthrough_block(
        [{"step": "login form", "phase": "start"}, {"step": "login form", "phase": "done"}]
    )
    assert "Making" in block
    assert "Done" in block


def test_cloud_suggest_only_for_long():
    assert wp.should_suggest_cloud("overnight migrate whole app") is True
    assert wp.should_suggest_cloud("fix typo in title") is False


def test_ship_gate_blocks_open_signup(tmp_path):
    (tmp_path / "app.py").write_text(
        'ALLOW_PUBLIC_REGISTRATION = "true"\nDEFAULT_ADMIN_PASSWORD = "admin123"\n',
        encoding="utf-8",
    )
    gate = wp.ship_gate(tmp_path)
    assert gate["security_ok"] is False
    assert gate["force"] is False
    assert "review" in gate["user_line"].lower() or "ship" in gate["user_line"].lower()


def test_ship_gate_clean_project(tmp_path):
    (tmp_path / "app.py").write_text("print('hi')\n", encoding="utf-8")
    gate = wp.ship_gate(tmp_path)
    assert gate["security_ok"] is True
    assert "yes" in gate["user_line"].lower()


def test_menu_and_features_cover_phase_d():
    ids = {f["id"] for f in wp.all_features()}
    for need in ("goal", "notifications", "cloud", "walkthrough", "review_gate", "sites"):
        assert need in ids
    menu = wp.plain_menu().lower()
    assert "goal" in menu
    assert "choose" in menu or "decide" in menu


def test_suggest_for_ship_mentions_review():
    lines = " ".join(wp.suggest_for_request("ship this to production")).lower()
    assert "review" in lines or "ship" in lines


def test_skills_carry_walkaway_rules():
    orch = (PLUGIN / "skills" / "orchestrator" / "SKILL.md").read_text(encoding="utf-8").lower()
    execute = (PLUGIN / "skills" / "execute" / "SKILL.md").read_text(encoding="utf-8").lower()
    verify = (PLUGIN / "skills" / "verify" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "/goal" in orch or "goal" in orch
    assert "cloud" in orch
    assert "walk" in execute or "narrate" in execute
    assert "review pane" in verify
    assert "sites" in orch or "host" in orch
