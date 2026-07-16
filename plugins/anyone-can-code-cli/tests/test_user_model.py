"""Improvement loop item 18: tiny user model. "About you" block grows ONLY
from explicit corrections; injected at session start within budget."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import state
import user_model


def test_correction_updates_profile(tmp_path):
    user_model.record_correction(tmp_path, "skill_level", "beginner")
    user_model.record_correction(tmp_path, "reply_taste", "short answers")
    prefs = state.read_preferences(tmp_path)
    assert prefs["about_you"]["skill_level"] == "beginner"
    assert prefs["about_you"]["reply_taste"] == "short answers"


def test_unknown_field_is_ignored(tmp_path):
    user_model.record_correction(tmp_path, "favorite_color", "blue")
    assert "favorite_color" not in state.read_preferences(tmp_path).get("about_you", {})


def test_profile_line_appears_in_session_context(tmp_path):
    import load_session

    user_model.record_correction(tmp_path, "stack", "Next.js + Supabase")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "About you" in ctx
    assert "Supabase" in ctx


def test_profile_line_stays_inside_budget(tmp_path):
    user_model.record_correction(tmp_path, "skill_level", "x" * 500)
    user_model.record_correction(tmp_path, "reply_taste", "y" * 500)
    user_model.record_correction(tmp_path, "stack", "z" * 500)
    line = user_model.about_you_line(tmp_path)
    assert len(line) <= user_model.LINE_MAX


def test_no_corrections_no_line(tmp_path):
    state.ensure_project_layout(tmp_path)
    assert user_model.about_you_line(tmp_path) == ""
