"""Item 19: SessionStart must not re-read every skills/*/SKILL.md."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import load_session


def test_load_session_source_does_not_open_skill_files():
    src = inspect.getsource(load_session)
    assert "skills/" not in src or "progressive" in src.lower()
    # must not glob all skill bodies
    assert "rglob" not in src or "notes" in src  # rglob ok for memory notes only
    assert "SKILL.md" not in src


def test_load_session_context_mentions_progressive_skills(tmp_path):
    ctx = load_session.build_context(tmp_path, "startup")
    assert "progressive" in ctx.lower() or "skill" in ctx.lower()
