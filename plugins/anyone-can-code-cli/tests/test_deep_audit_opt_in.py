"""Item 9: AI deep audit is opt-in, permission first, labeled hungry."""
from __future__ import annotations

from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def test_deep_audit_prompt_requires_permission():
    text = (PLUGIN / "automations" / "prompts" / "opt-in-deep-audit.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "permission" in text or "yes" in text
    assert "hungry" in text or "token" in text
    assert "do not change code" in text or "read-only" in text
    assert "off by default" in text or "opt-in" in text or "only schedule after" in text


def test_automations_readme_mentions_hungry_and_optional():
    text = (PLUGIN / "automations" / "README.md").read_text(encoding="utf-8").lower()
    assert "optional" in text
    assert "hungry" in text or "token" in text
