import yaml
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"

EXPLICIT_ONLY = {"orchestrator", "govern", "bridge", "memory-hygiene", "bite-plan", "cost-guard", "rule-suggest"}
IMPLICIT_OK = {"learn", "verify", "plan", "fix", "resume", "clarify", "capture"}


def test_explicit_only_skills_have_allow_implicit_false():
    for skill_name in EXPLICIT_ONLY:
        yaml_path = SKILLS_ROOT / skill_name / "agents" / "openai.yaml"
        assert yaml_path.exists(), f"Missing openai.yaml for {skill_name}"
        data = yaml.safe_load(yaml_path.read_text())
        policy = data.get("policy", {})
        assert policy.get("allow_implicit_invocation") is False, \
            f"{skill_name} should not auto-trigger"


def test_implicit_skills_have_openai_yaml():
    for skill_name in IMPLICIT_OK:
        yaml_path = SKILLS_ROOT / skill_name / "agents" / "openai.yaml"
        assert yaml_path.exists(), f"Missing openai.yaml for {skill_name}"
