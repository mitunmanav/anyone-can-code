"""Improvement loop item 17: answer "what did we decide about X?" from local
memory — notes + decisions + turn ledger — with dates. Pure text search, no deps.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import past_answer
import state


def test_seeded_decision_found_by_keyword_with_date(tmp_path):
    notes = state.ensure_project_layout(tmp_path)["memory_decisions"]
    notes.mkdir(parents=True, exist_ok=True)
    (notes / "2026-07-01.md").write_text(
        "- decided to use Stripe for payments\n", encoding="utf-8"
    )
    hits = past_answer.search_past(tmp_path, "what did we decide about stripe")
    assert hits, "seeded decision must be retrievable"
    assert "Stripe" in hits[0]["text"]
    assert hits[0]["date"] == "2026-07-01"


def test_turn_ledger_entry_found(tmp_path):
    ledger = state.ensure_project_layout(tmp_path)["state"] / "turn-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps({"ts": "2026-07-03T10:00:00Z", "summary": "picked Supabase database"})
        + "\n",
        encoding="utf-8",
    )
    hits = past_answer.search_past(tmp_path, "which database did we pick supabase")
    assert any("Supabase" in h["text"] for h in hits)


def test_no_match_returns_empty(tmp_path):
    state.ensure_project_layout(tmp_path)
    assert past_answer.search_past(tmp_path, "quantum blockchain llama") == []


def test_status_and_resume_skills_mention_past_answer():
    for name in ("status", "resume"):
        text = (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "past_answer" in text, f"{name} skill must route past questions"
        assert "date" in text.lower()
