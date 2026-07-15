"""Item 7: work / scheduled / self-improve loop registry."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import loop_registry as lr


def test_three_loops_present():
    ids = {x["id"] for x in lr.list_loops()}
    assert ids == {"work", "scheduled", "self_improve"}


def test_scheduled_is_opt_in_hungry():
    s = lr.describe_loop("scheduled")
    assert s is not None
    assert s["opt_in"] is True
    assert s["token"] == "hungry"


def test_self_improve_is_cheap():
    s = lr.describe_loop("self_improve")
    assert s is not None
    assert s["token"] == "cheap"
    assert "session_self_learn" in s["native"]


def test_plain_menu_nothing_forced():
    text = lr.plain_menu().lower()
    assert "choose" in text or "want" in text
    assert "off" in text or "skip" in text or "optional" in text


def test_automations_readme_says_optional():
    text = (PLUGIN / "automations" / "README.md").read_text(encoding="utf-8").lower()
    assert "optional" in text
    assert "ask" in text or "want" in text or "once" in text
