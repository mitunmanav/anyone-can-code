"""Safety item 27: browser test → Chrome, explain, user decides."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import browser_policy


def test_default_recommends_chrome_not_forced():
    advice = browser_policy.browser_test_advice()
    assert advice["recommended"] == "chrome"
    assert advice["tool"] == "@Chrome"
    assert advice["force"] is False
    low = advice["user_line"].lower()
    assert "chrome" in low
    assert "crash" in low or "safer" in low
    assert "choose" in low or "want" in low


def test_user_pref_builtin_still_not_forced():
    advice = browser_policy.browser_test_advice(user_prefers_builtin=True)
    assert advice["recommended"] == "builtin"
    assert advice["force"] is False


def test_verify_skill_prefers_chrome_not_self_browser():
    text = (PLUGIN / "skills" / "verify" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "chrome" in text
    assert "user decides" in text or "you choose" in text or "user picks" in text
    assert "crash" in text or "safer" in text
