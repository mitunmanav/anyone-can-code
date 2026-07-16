"""Improvement loop item 1: dictated prompts route the same as typed ones.

Codex Desktop ships voice dictation (Ctrl+M) — transcripts arrive with
filler words, stutter repeats, and no punctuation. Routing must not care.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import front_door


PAIRS = [
    ("fix the login bug", "um so the the login bug uh fix it please"),
    ("I want to build a website with auth", "so um i want to build a website you know with auth"),
    ("add dark mode feature", "uh can you add dark mode feature please please"),
    ("verify and ship this", "umm verify and uh ship this"),
]


def test_dictated_prompt_routes_like_typed():
    for clean, dictated in PAIRS:
        assert front_door.classify_entry_mode(clean) == front_door.classify_entry_mode(dictated), (
            f"route drifted for: {dictated!r}"
        )


def test_normalize_strips_filler_and_stutter():
    out = front_door.normalize_text("um so the the login is uh uh broken you know")
    assert "um" not in out.split()
    assert "uh" not in out.split()
    assert "the the" not in out


def test_normalize_keeps_real_words():
    out = front_door.normalize_text("I would like a simple website")
    assert "like" in out  # 'like' is a real verb here, never strip it
    assert "simple website" in out
