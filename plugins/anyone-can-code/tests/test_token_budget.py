"""Improvement loop item 14: the plugin's own text must stay small.

Skill docs and hook injections ride every session — oversized text is a
recurring token tax on the user. Doctor enforces the budget.
"""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import doctor


SKILL_BUDGET = 4000


def test_doctor_flags_oversized_skill(tmp_path):
    skill = tmp_path / "skills" / "bloated" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("x" * (SKILL_BUDGET + 1), encoding="utf-8")
    results = doctor.run_skill_budget(skills_root=tmp_path / "skills")
    assert any(r["status"] == "FAIL" for r in results)


def test_doctor_passes_small_skill(tmp_path):
    skill = tmp_path / "skills" / "tiny" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("small skill", encoding="utf-8")
    results = doctor.run_skill_budget(skills_root=tmp_path / "skills")
    assert all(r["status"] == "PASS" for r in results)


def test_all_shipped_skills_fit_budget():
    results = doctor.run_skill_budget()
    over = [r for r in results if r["status"] == "FAIL"]
    assert not over, f"skills over budget: {[r['detail'] for r in over]}"


def test_turn_context_hard_capped(tmp_path):
    import guard

    huge_prompt = "\n".join(f"- idea number {i} with plenty of words" for i in range(40))
    ctx = guard.build_turn_context(huge_prompt, tmp_path)
    assert len(ctx) <= guard.MAX_TURN_CONTEXT_CHARS
