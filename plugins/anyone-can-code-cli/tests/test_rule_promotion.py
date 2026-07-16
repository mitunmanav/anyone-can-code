"""Improvement loop item 16: lesson repeated 3+ times -> propose permanent rule once.

No auto-promotion: user must say yes; approved rules land in memory/rules.md
and get injected at session start.
"""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import rule_promote
import state


def _write_lessons(repo_root: Path, lesson: str, times: int) -> None:
    notes = state.ensure_project_layout(repo_root)["memory_lessons"]
    notes.mkdir(parents=True, exist_ok=True)
    for i in range(times):
        (notes / f"note-{i}.md").write_text(f"- {lesson}\n", encoding="utf-8")


def test_three_repeats_generate_one_proposal(tmp_path):
    _write_lessons(tmp_path, "Always run npm.cmd on Windows", 3)
    first = rule_promote.pending_proposals(tmp_path)
    assert len(first) == 1
    assert "3" in first[0] and "yes" in first[0].lower()
    # proposed once — second scan proposes nothing new
    assert rule_promote.pending_proposals(tmp_path) == []


def test_two_repeats_generate_nothing(tmp_path):
    _write_lessons(tmp_path, "Check terminal before claiming done", 2)
    assert rule_promote.pending_proposals(tmp_path) == []


def test_approve_writes_rule_no_auto_promotion(tmp_path):
    _write_lessons(tmp_path, "Reread file before patch retry", 3)
    rules_file = state.ensure_project_layout(tmp_path)["memory"] / "rules.md"
    rule_promote.pending_proposals(tmp_path)
    assert not rules_file.exists()  # proposal alone must not promote
    rule_promote.approve(tmp_path, "Reread file before patch retry")
    assert "Reread file before patch retry" in rules_file.read_text(encoding="utf-8")


def test_session_start_injects_approved_rules(tmp_path):
    import load_session

    rule_promote.approve(tmp_path, "Always run npm.cmd on Windows")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "npm.cmd" in ctx


def test_learn_skill_mentions_promotion():
    text = (PLUGIN / "skills" / "learn" / "SKILL.md").read_text(encoding="utf-8")
    low = text.lower()
    assert "promote" in low
    assert "3" in text
    assert "yes" in low and "no" in low  # user decides
