"""Skill UI labels: Codex docs use agents/openai.yaml display_name for the app."""

from __future__ import annotations

from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"

# Short labels shown in Codex Desktop (not the $invoke name).
EXPECTED = {
    "setup": "ACC setup",
    "orchestrator": "ACC home",
    "onboard": "ACC start",
    "clarify": "ACC clarify",
    "plan": "ACC plan",
    "execute": "ACC build",
    "verify": "ACC check",
    "fix": "ACC fix",
    "resume": "ACC resume",
    "handoff": "ACC handoff",
    "status": "ACC status",
    "help": "ACC help",
    "settings": "ACC settings",
    "update": "ACC update",
    "usage": "ACC usage",
    "learn": "ACC learn",
    "capture": "ACC note",
    "wiki": "ACC wiki",
    "readable": "ACC clear",
    "govern": "ACC scope",
    "bridge": "ACC plugins",
    "council": "ACC council",
    "skeptic": "ACC skeptic",
    "parallel-fix": "ACC parallel fix",
    "roster": "ACC roster",
    "oneshot": "ACC strong run",
    "checkpoint": "ACC checkpoint",
    "rule-suggest": "ACC rule suggest",
    "cost-guard": "ACC cost guard",
    "bite-plan": "ACC bite plan",
    "memory-hygiene": "ACC memory hygiene",
}


def test_every_skill_has_acc_display_name() -> None:
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    assert skill_dirs, "no skills found"
    missing = []
    for skill_dir in skill_dirs:
        yaml_path = skill_dir / "agents" / "openai.yaml"
        if not yaml_path.is_file():
            missing.append(f"{skill_dir.name}: missing agents/openai.yaml")
            continue
        text = yaml_path.read_text(encoding="utf-8")
        expected = EXPECTED.get(skill_dir.name)
        if expected is None:
            missing.append(f"{skill_dir.name}: not in EXPECTED map")
            continue
        if f'display_name: "{expected}"' not in text:
            missing.append(f"{skill_dir.name}: want display_name {expected!r}")
        if "short_description:" not in text:
            missing.append(f"{skill_dir.name}: missing short_description")
    assert not missing, "\n".join(missing)


def test_skill_invoke_name_stays_short_folder_name() -> None:
    """$setup etc. stay as frontmatter name — display_name is UI only."""
    for folder in EXPECTED:
        skill_md = (SKILLS / folder / "SKILL.md").read_text(encoding="utf-8")
        assert f"name: {folder}" in skill_md, folder
