"""$rule-suggest: fingerprint repeated lessons/keywords; suggest only (no write).

Deep-research feature: Cursor-style durable rule/skill proposals when patterns
repeat. User must say YES before wiki/learn note or AGENTS.md bullet write.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import rule_suggest


def _write_note(root: Path, name: str, body: str) -> None:
    notes = root / ".codex" / "anyone-can-code" / "memory" / "notes" / "lessons"
    notes.mkdir(parents=True, exist_ok=True)
    (notes / name).write_text(body, encoding="utf-8")


def _write_prompt_log(root: Path, prompts: list[str]) -> None:
    state = root / ".codex" / "anyone-can-code" / "state"
    state.mkdir(parents=True, exist_ok=True)
    path = state / "prompt-log.jsonl"
    lines = [json.dumps({"prompt": p}) for p in prompts]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_fingerprint_normalizes_noise():
    a = rule_suggest.fingerprint("Always run npm.cmd on Windows!")
    b = rule_suggest.fingerprint("always run  npm.cmd  on windows")
    assert a == b
    assert a  # non-empty


def test_three_note_repeats_yield_suggestion(tmp_path):
    lesson = "Always run npm.cmd on Windows"
    for i in range(3):
        _write_note(tmp_path, f"n{i}.md", f"- {lesson}\n")
    suggestions = rule_suggest.suggest_rules(tmp_path)
    assert len(suggestions) >= 1
    top = suggestions[0]
    assert top["count"] >= 3
    assert "npm" in top["sample"].lower() or "npm" in top["fingerprint"]
    assert top["wiki_note"]
    assert top["agents_bullet"]
    assert "notes" in top["sources"]


def test_two_repeats_yield_nothing(tmp_path):
    for i in range(2):
        _write_note(tmp_path, f"n{i}.md", "- Check terminal before claiming done\n")
    assert rule_suggest.suggest_rules(tmp_path) == []


def test_prompt_log_repeats_yield_suggestion(tmp_path):
    prompt = "fix the npm path again — still wrong on Windows"
    _write_prompt_log(tmp_path, [prompt] * 3)
    suggestions = rule_suggest.suggest_rules(tmp_path)
    assert len(suggestions) >= 1
    assert "prompt-log" in suggestions[0]["sources"]
    assert suggestions[0]["count"] >= 3


def test_empty_project_returns_empty(tmp_path):
    assert rule_suggest.suggest_rules(tmp_path) == []


def test_suggest_never_writes(tmp_path):
    lesson = "Reread file before patch retry"
    for i in range(3):
        _write_note(tmp_path, f"n{i}.md", f"- {lesson}\n")
    before = list((tmp_path / ".codex").rglob("*"))
    rule_suggest.suggest_rules(tmp_path)
    after = list((tmp_path / ".codex").rglob("*"))
    assert before == after
    agents = tmp_path / "AGENTS.md"
    assert not agents.exists()


def test_skill_yaml_registration():
    skill_dir = PLUGIN / "skills" / "rule-suggest"
    skill_md = skill_dir / "SKILL.md"
    yaml_path = skill_dir / "agents" / "openai.yaml"
    assert skill_md.is_file()
    text = skill_md.read_text(encoding="utf-8")
    assert 'name: rule-suggest' in text
    assert text.startswith("---")
    assert 'description: "Use ' in text
    assert "yes" in text.lower()
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert data["interface"]["display_name"] == "ACC rule suggest"
    policy = data.get("policy") or {}
    assert policy.get("allow_implicit_invocation") is False


def test_skill_mentions_helper_and_no_auto_write():
    text = (PLUGIN / "skills" / "rule-suggest" / "SKILL.md").read_text(encoding="utf-8")
    low = text.lower()
    assert "rule_suggest.py" in text or "rule_suggest" in text
    assert "agents.md" in low
    assert "yes" in low
    assert "never" in low or "not write" in low or "no write" in low
