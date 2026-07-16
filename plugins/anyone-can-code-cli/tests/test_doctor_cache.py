"""Backlog 4: doctor must detect stale duplicate plugin cache and missing skills.

Real trial root cause: two cache versions were live at once and the
orchestrator skill vanished mid-session.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import doctor

PLUGIN_SKILLS = Path(__file__).resolve().parents[1] / "skills"


def _make_cache(tmp_path: Path, versions: dict[str, list[str]]) -> Path:
    """Build fake cache: version dir name -> list of skill folder names."""
    plugin_cache = tmp_path / "cache" / "acc-marketplace" / "anyone-can-code"
    for version, skills in versions.items():
        for skill in skills:
            skill_dir = plugin_cache / version / "skills" / skill
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("stub", encoding="utf-8")
    return tmp_path / "cache"


def _statuses(instance: doctor.Doctor) -> dict[str, str]:
    return {row["check"]: row["status"] for row in instance.results}


def test_duplicate_cache_versions_warn(tmp_path):
    repo_skills = [p.name for p in PLUGIN_SKILLS.iterdir() if p.is_dir()]
    cache_root = _make_cache(tmp_path, {
        "1.0.0": repo_skills,
        "1.0.0+codex.20260613": repo_skills,
    })

    instance = doctor.Doctor(json_mode=True)
    instance.run_plugin_cache(cache_root=cache_root)

    statuses = _statuses(instance)
    assert statuses.get("plugin_cache_versions") == "WARN"


def test_cache_missing_skills_fails(tmp_path):
    repo_skills = [p.name for p in PLUGIN_SKILLS.iterdir() if p.is_dir()]
    incomplete = [s for s in repo_skills if s != "orchestrator"]
    cache_root = _make_cache(tmp_path, {"1.0.0": incomplete})

    instance = doctor.Doctor(json_mode=True)
    instance.run_plugin_cache(cache_root=cache_root)

    statuses = _statuses(instance)
    assert statuses.get("plugin_cache_skills") == "FAIL"
    evidence = next(
        r["evidence"] for r in instance.results if r["check"] == "plugin_cache_skills"
    )
    assert "orchestrator" in evidence


def test_single_complete_cache_passes(tmp_path):
    repo_skills = [p.name for p in PLUGIN_SKILLS.iterdir() if p.is_dir()]
    cache_root = _make_cache(tmp_path, {"1.0.0": repo_skills})

    instance = doctor.Doctor(json_mode=True)
    instance.run_plugin_cache(cache_root=cache_root)

    statuses = _statuses(instance)
    assert statuses.get("plugin_cache_versions") == "PASS"
    assert statuses.get("plugin_cache_skills") == "PASS"


def test_no_cache_is_informational(tmp_path):
    instance = doctor.Doctor(json_mode=True)
    instance.run_plugin_cache(cache_root=tmp_path / "does-not-exist")

    statuses = _statuses(instance)
    assert statuses.get("plugin_cache_versions") == "PASS"
