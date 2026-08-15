"""EFFICIENCY mode — cheap/fast inject flags (deep-research spirit).

Honest: soft tips only; never forces host model picker APIs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import efficiency_mode
import model_ledger
import load_session
import state


def test_env_acc_efficiency_on(monkeypatch):
    monkeypatch.setenv("ACC_EFFICIENCY", "1")
    monkeypatch.delenv("ACC_LOAD_LEAN", raising=False)
    assert efficiency_mode.is_on({}) is True
    flags = efficiency_mode.flags({})
    assert flags["efficiency"] is True
    assert flags["skip_tier_c"] is True
    assert flags["skip_verbose_receipts"] is True
    assert flags["prefer_short_skills"] is True
    assert flags["max_inject_chars"] < efficiency_mode.DEFAULT_SOFT_CAP


def test_prefs_lean_true_without_env(monkeypatch):
    monkeypatch.delenv("ACC_EFFICIENCY", raising=False)
    monkeypatch.delenv("ACC_LOAD_LEAN", raising=False)
    assert efficiency_mode.is_on({"lean": True}) is True
    assert efficiency_mode.is_on({"efficiency": True}) is True
    assert efficiency_mode.is_on({"lean": "true"}) is True
    assert efficiency_mode.is_on({}) is False


def test_acc_load_lean_unifies_as_efficiency(monkeypatch):
    monkeypatch.delenv("ACC_EFFICIENCY", raising=False)
    monkeypatch.setenv("ACC_LOAD_LEAN", "1")
    flags = efficiency_mode.flags({})
    assert flags["efficiency"] is True
    assert flags["skip_tier_c"] is True
    assert flags["load_lean"] is True


def test_caps_and_flag_shape():
    off = efficiency_mode.flags({}, environ={})
    assert off["max_inject_chars"] == efficiency_mode.DEFAULT_SOFT_CAP
    assert off["skip_tier_c"] is False
    on = efficiency_mode.flags({}, environ={"ACC_EFFICIENCY": "1"})
    assert on["max_inject_chars"] == efficiency_mode.EFFICIENCY_SOFT_CAP
    assert on["max_inject_chars"] < off["max_inject_chars"]


def test_load_session_prefs_lean_skips_tier_c(tmp_path, monkeypatch):
    monkeypatch.delenv("ACC_EFFICIENCY", raising=False)
    monkeypatch.delenv("ACC_LOAD_LEAN", raising=False)
    state.ensure_project_layout(tmp_path)
    state.write_preferences(tmp_path, {"lean": True, "communication_mode": "caveman-strict"})
    ctx = load_session.build_context(tmp_path, "startup")
    assert "ENFORCE comm rule" in ctx
    assert "ACC_PLUGIN_ROOT=" in ctx
    assert "Loops:" not in ctx
    assert "Efficiency:" in ctx or "lean" in ctx.lower()


def test_load_session_efficiency_env_skips_verbose_receipts(tmp_path, monkeypatch):
    monkeypatch.setenv("ACC_EFFICIENCY", "1")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Loops:" not in ctx
    # verbose observability parade stays out of lean inject
    assert "What AI did: nothing recorded yet for this project." not in ctx


def test_model_ledger_soft_tip_when_efficiency(tmp_path):
    path = tmp_path / "led.jsonl"
    model_ledger.record_model_result("gpt-5.6", "feature", "success", ledger_path=path)
    model_ledger.record_model_result("gpt-5.6-luna", "feature", "success", ledger_path=path)
    model_ledger.record_model_result("gpt-5.6-luna", "feature", "success", ledger_path=path)
    rec = model_ledger.recommend_model("feature", ledger_path=path, efficiency=True)
    assert rec.get("soft") is True
    assert "tip" in rec
    assert "soft" in rec["tip"].lower() or "suggest" in rec["tip"].lower()
    # cheaper label preferred when it wins or ties
    assert "luna" in rec["model"].lower() or "luna" in rec["tip"].lower()
    assert "host" in rec["tip"].lower() or "picker" in rec["tip"].lower()


def test_model_ledger_no_force_without_efficiency(tmp_path):
    path = tmp_path / "led.jsonl"
    model_ledger.record_model_result("gpt-5.6", "general", "success", ledger_path=path)
    rec = model_ledger.recommend_model("general", ledger_path=path, efficiency=False)
    assert rec.get("soft") is not True
    assert not rec.get("tip")


def test_model_cost_class_labels():
    assert model_ledger.model_cost_class("gpt-5.6-luna") == "cheap"
    assert model_ledger.model_cost_class("something-mini") == "cheap"
    assert model_ledger.model_cost_class("gpt-5.6-sol") == "hungry"
    assert model_ledger.model_cost_class("claude-opus-4") == "hungry"


def test_skill_and_settings_document_efficiency():
    skill = (PLUGIN / "skills" / "efficiency" / "SKILL.md").read_text(encoding="utf-8")
    assert "ACC_EFFICIENCY" in skill
    assert "lean" in skill.lower()
    assert "soft" in skill.lower()
    assert "picker" in skill.lower() or "never force" in skill.lower()
    settings = (PLUGIN / "skills" / "settings" / "SKILL.md").read_text(encoding="utf-8")
    assert "lean" in settings.lower() or "efficiency" in settings.lower()
