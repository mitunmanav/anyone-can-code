"""Improvement loop item 15: Karpathy guardrails ride the turn context.

Four one-line rules against the classic LLM coding failures: hidden
assumptions, overbuilt code, orthogonal edits, unverifiable "done".
Injected via hooks so they cannot vanish with the skills-list cap.
"""

from __future__ import annotations

import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))

import guard


def test_turn_context_carries_all_four_guardrails(tmp_path):
    ctx = guard.build_turn_context("add a login page", tmp_path).lower()
    assert "assumption" in ctx, "rule 1 missing: surface assumptions"
    assert "simplest" in ctx, "rule 2 missing: simplicity first"
    assert "only" in ctx and "task" in ctx, "rule 3 missing: surgical changes"
    assert "verify" in ctx, "rule 4 missing: goal-driven verification"


def test_guardrails_fit_the_budget(tmp_path):
    ctx = guard.build_turn_context("add a login page", tmp_path)
    assert len(ctx) <= guard.MAX_TURN_CONTEXT_CHARS
