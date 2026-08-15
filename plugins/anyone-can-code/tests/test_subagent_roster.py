"""$roster: suggest Codex subagent role prompts (explorer/worker/reviewer).

Prompts only — never write .codex/agents/*.toml. Doc-verified against Codex
built-ins (explorer/worker/default) + custom agent pattern (name, description,
developer_instructions). Copilot analog: agent profiles = role prompts, not ACC
auto-write.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import subagent_roster


def test_default_roster_has_three_core_roles():
    roles = subagent_roster.suggest_roster()
    names = [r["role"] for r in roles]
    assert names == ["explorer", "worker", "reviewer"]


def test_each_role_has_spawn_prompt_and_scope():
    for role in subagent_roster.suggest_roster():
        assert role["role"]
        assert role["agent_type"]
        assert role["scope"] in ("read-only", "read-write")
        assert role["when"]
        prompt = role["spawn_prompt"]
        assert "Spawn a subagent" in prompt
        for token in ("Job:", "Scope:", "Expected output:"):
            assert token in prompt, f"{role['role']} missing {token}"
        assert "caveman" in prompt.lower()


def test_explorer_is_read_only_worker_is_read_write():
    by_name = {r["role"]: r for r in subagent_roster.suggest_roster()}
    assert by_name["explorer"]["scope"] == "read-only"
    assert by_name["explorer"]["agent_type"] == "explorer"
    assert by_name["worker"]["scope"] == "read-write"
    assert by_name["worker"]["agent_type"] == "worker"
    assert by_name["reviewer"]["scope"] == "read-only"


def test_goal_fills_job_in_prompts():
    roles = subagent_roster.suggest_roster(
        goal="map auth flow",
        scope_hint="src/auth/",
    )
    for role in roles:
        assert "map auth flow" in role["spawn_prompt"]
        assert "src/auth/" in role["spawn_prompt"]


def test_filter_roles():
    roles = subagent_roster.suggest_roster(roles=["explorer", "reviewer"])
    assert [r["role"] for r in roles] == ["explorer", "reviewer"]


def test_unknown_role_ignored():
    roles = subagent_roster.suggest_roster(roles=["explorer", "wizard"])
    assert [r["role"] for r in roles] == ["explorer"]


def test_toml_snippet_is_text_only_optional():
    """Optional pasteable TOML for custom agents — helper never writes it."""
    roles = subagent_roster.suggest_roster()
    for role in roles:
        snippet = role.get("toml_snippet") or ""
        if role["role"] == "reviewer":
            # reviewer is not a Codex built-in — snippet helps user who wants
            # a project custom agent file (user pastes; ACC does not write).
            assert 'name = "reviewer"' in snippet
            assert "developer_instructions" in snippet
        # Never claim a write path as done
        assert "wrote" not in (role.get("note") or "").lower()


def test_suggest_never_writes(tmp_path):
    before = list(tmp_path.rglob("*"))
    subagent_roster.suggest_roster(goal="anything")
    subagent_roster.main(
        ["--json", "--goal", "x", "--project-root", str(tmp_path)]
    )
    after = list(tmp_path.rglob("*"))
    assert before == after
    assert not (tmp_path / ".codex").exists()


def test_cli_json(capsys):
    code = subagent_roster.main(["--json", "--goal", "review branch"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["count"] == 3
    assert len(data["roles"]) == 3
    assert data["roles"][0]["role"] == "explorer"
    assert "review branch" in data["roles"][0]["spawn_prompt"]


def test_cli_text_mode(capsys):
    code = subagent_roster.main(["--roles", "worker"])
    assert code == 0
    out = capsys.readouterr().out
    assert "worker" in out.lower()
    assert "Spawn a subagent" in out


def test_skill_yaml_registration():
    skill_dir = PLUGIN / "skills" / "roster"
    skill_md = skill_dir / "SKILL.md"
    yaml_path = skill_dir / "agents" / "openai.yaml"
    assert skill_md.is_file()
    text = skill_md.read_text(encoding="utf-8")
    assert "name: roster" in text
    assert text.startswith("---")
    assert 'description: "Use ' in text
    assert "subagent_roster" in text or "subagent_roster.py" in text
    assert "Spawn a subagent" in text
    low = text.lower()
    assert "never write" in low or "prompts only" in low or "suggest only" in low
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert data["interface"]["display_name"] == "ACC roster"
    policy = data.get("policy") or {}
    assert policy.get("allow_implicit_invocation") is False


def test_skill_under_budget():
    size = len((PLUGIN / "skills" / "roster" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
