"""Improvement loop item 13: idea dump inbox.

User dumps many thoughts in one message -> each distinct item recorded locally,
count surfaced, repeats deduped with a pointer to the existing entry.
"""

from __future__ import annotations

import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))

import inbox


DUMP = """ideas for the app:
- login with google
- dark mode toggle
- export data as csv
"""


def test_dump_records_all_items(tmp_path):
    result = inbox.process_prompt(DUMP, tmp_path)
    assert result["new"] == 3
    assert result["total"] == 3
    text = inbox.inbox_path(tmp_path).read_text(encoding="utf-8")
    for item in ("login with google", "dark mode toggle", "export data as csv"):
        assert item in text


def test_context_is_caveman_short_with_count(tmp_path):
    result = inbox.process_prompt(DUMP, tmp_path)
    ctx = result["context"]
    assert "3" in ctx  # count surfaced
    assert len(ctx) <= 200, f"context too long: {len(ctx)}"


def test_repeat_item_deduped_with_pointer(tmp_path):
    inbox.process_prompt(DUMP, tmp_path)
    result = inbox.process_prompt("- dark mode toggle\n- login with google\n", tmp_path)
    assert result["new"] == 0
    assert result["total"] == 3
    assert "already" in result["context"].lower()


def test_near_duplicate_is_caught(tmp_path):
    inbox.process_prompt(DUMP, tmp_path)
    result = inbox.process_prompt("- add a dark mode toggle please\n- csv data export\n", tmp_path)
    assert result["new"] == 0


def test_plain_prompt_does_not_trigger(tmp_path):
    result = inbox.process_prompt("fix the login bug", tmp_path)
    assert result["new"] == 0
    assert result["context"] == ""
    assert not inbox.inbox_path(tmp_path).exists()


def test_guard_turn_context_carries_inbox_line(tmp_path):
    import guard

    ctx = guard.build_turn_context(DUMP, tmp_path)
    assert "Inbox: got 3 new" in ctx


def test_mixed_dump_only_new_recorded(tmp_path):
    inbox.process_prompt(DUMP, tmp_path)
    result = inbox.process_prompt("- dark mode toggle\n- push notifications\n", tmp_path)
    assert result["new"] == 1
    assert result["total"] == 4
