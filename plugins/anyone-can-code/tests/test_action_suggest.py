"""Improvement loop item 10: $setup suggests one-click action buttons.

Doc-verified (app/local-environments.md): actions are defined by the user in
app Settings and run in the integrated terminal — so ACC suggests, never writes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import action_suggest


def test_node_project_gets_npm_actions(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"test": "jest", "dev": "next dev"}}), encoding="utf-8"
    )
    actions = action_suggest.suggest_actions(tmp_path)
    scripts = [a["script"] for a in actions]
    assert "npm test" in scripts
    assert "npm run dev" in scripts


def test_python_project_gets_pytest_action(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    actions = action_suggest.suggest_actions(tmp_path)
    assert any("pytest" in a["script"] for a in actions)


def test_unknown_project_gets_no_suggestions(tmp_path):
    assert action_suggest.suggest_actions(tmp_path) == []


def test_every_suggestion_is_plain_worded(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {"test": "jest"}}), encoding="utf-8")
    for action in action_suggest.suggest_actions(tmp_path):
        assert action["name"]
        assert action["why"], "each button needs a plain-words reason"


def test_setup_skill_mentions_actions():
    text = (PLUGIN / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    assert "action" in text.lower()
    assert "suggest" in text.lower()
    assert "never" in text.lower()  # never auto-write app settings
