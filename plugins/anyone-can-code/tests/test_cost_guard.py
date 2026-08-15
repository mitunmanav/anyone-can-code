"""Soft model-tier tips for $cost-guard (Luna / Terra / Sol)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import cost_guard  # noqa: E402

SKILLS = PLUGIN / "skills"
SKILL_DIR = SKILLS / "cost-guard"


def test_recommend_luna_for_micro_clear_work() -> None:
    rec = cost_guard.recommend("rename a variable and fix lint")
    assert rec["tier"] == "luna"
    assert rec["model_id"] == "gpt-5.6-luna"
    assert "cannot force" in rec["honesty"].lower() or "cannot" in rec["honesty"].lower()


def test_recommend_terra_for_everyday_feature() -> None:
    rec = cost_guard.recommend("add a small feature and fix a bug in one file")
    assert rec["tier"] == "terra"
    assert rec["model_id"] == "gpt-5.6-terra"


def test_recommend_sol_for_hard_open_work() -> None:
    rec = cost_guard.recommend("hard architecture redesign and security audit research")
    assert rec["tier"] == "sol"
    assert rec["model_id"] == "gpt-5.6-sol"


def test_recommend_default_terra_when_unknown() -> None:
    rec = cost_guard.recommend("do the thing")
    assert rec["tier"] == "terra"
    assert rec["model_id"] == "gpt-5.6-terra"


def test_recommend_includes_prices_and_tip() -> None:
    rec = cost_guard.recommend("classify rows and extract fields")
    assert "prices" in rec
    assert rec["prices"]["input_per_1m"] is not None
    assert rec["prices"]["output_per_1m"] is not None
    assert rec["tip"]
    assert "luna" in rec["tip"].lower() or "model" in rec["tip"].lower()
    assert rec["as_of"]


def test_honesty_always_present() -> None:
    for task in ("lint", "feature", "security research", ""):
        rec = cost_guard.recommend(task)
        assert "ACC cannot force" in rec["honesty"] or "cannot force Codex" in rec["honesty"]


def test_classify_task_keywords() -> None:
    assert cost_guard.classify_task("format and rename") == "luna"
    assert cost_guard.classify_task("implement feature fix bug") == "terra"
    assert cost_guard.classify_task("ambiguous architecture security") == "sol"


def test_tier_catalog_has_three() -> None:
    tiers = cost_guard.tier_catalog()
    ids = {t["model_id"] for t in tiers}
    assert ids == {"gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"}
    for t in tiers:
        assert t["input_per_1m"] >= 0
        assert t["output_per_1m"] >= 0


def test_format_card_contains_honesty_and_tier() -> None:
    card = cost_guard.format_card("quick classify extract")
    assert "ACC cannot force" in card or "cannot force Codex" in card
    assert "Luna" in card or "luna" in card
    assert "WHERE" in card or "TIER" in card or "TIP" in card


def test_cli_json_recommend(capsys) -> None:
    code = cost_guard.main(["--json", "rename and lint only"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tier"] == "luna"
    assert payload["model_id"] == "gpt-5.6-luna"


def test_cli_catalog_json(capsys) -> None:
    code = cost_guard.main(["--json", "--catalog"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["tiers"]) == 3


def test_skill_files_exist_and_explicit_only() -> None:
    skill_md = SKILL_DIR / "SKILL.md"
    yaml_path = SKILL_DIR / "agents" / "openai.yaml"
    assert skill_md.is_file(), "missing cost-guard/SKILL.md"
    assert yaml_path.is_file(), "missing cost-guard/agents/openai.yaml"
    text = skill_md.read_text(encoding="utf-8")
    assert "name: cost-guard" in text
    assert "cannot force" in text.lower() or "cannot switch" in text.lower()
    yml = yaml_path.read_text(encoding="utf-8")
    assert 'display_name: "ACC cost guard"' in yml
    assert "allow_implicit_invocation: false" in yml


def test_skill_under_budget() -> None:
    size = len((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"SKILL.md too large: {size}"
