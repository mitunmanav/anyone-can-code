"""ACC approval grades: off|ask|allowlist|strict → guard behavior hints.

Does NOT invent Codex host APIs. Grades are ACC prefs + hints for audit/guard.
Analog research: Cursor run modes, Windsurf auto-exec levels, Codex sandbox/approvals.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import approval_grades as ag


def test_grades_are_exact_four():
    assert ag.GRADES == ("off", "ask", "allowlist", "strict")
    assert ag.DEFAULT_GRADE == "ask"


def test_normalize_grade_accepts_aliases():
    assert ag.normalize_grade("ASK") == "ask"
    assert ag.normalize_grade(" allow-list ") == "allowlist"
    assert ag.normalize_grade("allow_list") == "allowlist"
    assert ag.normalize_grade("strict") == "strict"
    assert ag.normalize_grade("off") == "off"
    assert ag.normalize_grade("bogus") == ag.DEFAULT_GRADE
    assert ag.normalize_grade(None) == ag.DEFAULT_GRADE


def test_grade_from_prefs_defaults_ask():
    assert ag.grade_from_prefs({}) == "ask"
    assert ag.grade_from_prefs({"approval_mode": "strict"}) == "strict"
    assert ag.grade_from_prefs({"approval_mode": "Allowlist"}) == "allowlist"


def test_guard_hints_off_disables_acc_auto_allow():
    h = ag.guard_hints("off")
    assert h["layer_active"] is False
    assert h["auto_allow_safe_reads"] is False
    assert h["auto_allow_safe_bash"] is False
    assert h["use_user_allowlist"] is False
    assert h["force_prompt"] is True


def test_guard_hints_ask_matches_current_spam_killer():
    h = ag.guard_hints("ask")
    assert h["layer_active"] is True
    assert h["auto_allow_safe_reads"] is True
    assert h["auto_allow_safe_bash"] is True
    assert h["use_user_allowlist"] is False
    assert h["force_prompt"] is False
    assert h["extra_caution"] is False


def test_guard_hints_allowlist_uses_list_not_safe_bash():
    h = ag.guard_hints("allowlist")
    assert h["layer_active"] is True
    assert h["auto_allow_safe_reads"] is True
    assert h["auto_allow_safe_bash"] is False
    assert h["use_user_allowlist"] is True
    assert h["force_prompt"] is False


def test_guard_hints_strict_never_auto():
    h = ag.guard_hints("strict")
    assert h["layer_active"] is True
    assert h["auto_allow_safe_reads"] is False
    assert h["auto_allow_safe_bash"] is False
    assert h["use_user_allowlist"] is False
    assert h["force_prompt"] is True
    assert h["extra_caution"] is True


def test_describe_grade_plain_words_and_codex_boundary():
    for grade in ag.GRADES:
        d = ag.describe_grade(grade)
        assert d["grade"] == grade
        assert d["user_line"]
        assert d["agent_line"]
        assert "codex" in d["codex_boundary"].lower()
        # Must not claim ACC sets Codex host flags
        low = (d["user_line"] + d["agent_line"] + d["codex_boundary"]).lower()
        assert "--ask-for-approval" not in low
        assert "danger-full-access" not in low or "user sets" in low or "host" in low


def test_command_matches_allowlist_prefix():
    allow = ["git status", "pytest", "python -m pytest"]
    assert ag.command_matches_allowlist("git status", allow) is True
    assert ag.command_matches_allowlist("git status -sb", allow) is True
    assert ag.command_matches_allowlist("python -m pytest -q", allow) is True
    assert ag.command_matches_allowlist("git push", allow) is False
    assert ag.command_matches_allowlist("rm -rf /", allow) is False


def test_should_auto_allow_ask_uses_safe_fn():
    def safe(name, inp):
        return name == "Read" or (
            name == "Bash" and str((inp or {}).get("command", "")).startswith("git status")
        )

    assert ag.should_auto_allow("ask", "Read", {}, is_safe_fn=safe) is True
    assert ag.should_auto_allow(
        "ask", "Bash", {"command": "git status"}, is_safe_fn=safe
    ) is True
    assert ag.should_auto_allow(
        "ask", "Bash", {"command": "rm -rf x"}, is_safe_fn=safe
    ) is False


def test_should_auto_allow_off_and_strict_never():
    def safe(_n, _i):
        return True

    assert ag.should_auto_allow("off", "Read", {}, is_safe_fn=safe) is False
    assert ag.should_auto_allow("strict", "Read", {}, is_safe_fn=safe) is False
    assert ag.should_auto_allow(
        "strict", "Bash", {"command": "git status"}, is_safe_fn=safe
    ) is False


def test_should_auto_allow_allowlist_mode():
    def safe(name, inp):
        # Safe reads only — bash not in default safe set for this stub
        return name == "Read"

    allow = ["git status"]
    assert ag.should_auto_allow(
        "allowlist", "Read", {}, is_safe_fn=safe, allowlist=allow
    ) is True
    assert ag.should_auto_allow(
        "allowlist",
        "Bash",
        {"command": "git status -sb"},
        is_safe_fn=safe,
        allowlist=allow,
    ) is True
    assert ag.should_auto_allow(
        "allowlist",
        "Bash",
        {"command": "python -m pytest"},
        is_safe_fn=safe,
        allowlist=allow,
    ) is False
    assert ag.should_auto_allow(
        "allowlist",
        "Bash",
        {"command": "git status"},
        is_safe_fn=safe,
        allowlist=[],
    ) is False


def test_set_grade_and_allowlist_on_prefs():
    prefs: dict = {}
    prefs = ag.set_grade(prefs, "strict")
    assert prefs["approval_mode"] == "strict"
    prefs = ag.set_allowlist(prefs, ["git status", "  pytest  ", ""])
    assert prefs["approval_allowlist"] == ["git status", "pytest"]


def test_apply_grade_writes_preferences(tmp_path):
    import state

    out = ag.apply_grade(tmp_path, "allowlist", allowlist=["git status"])
    assert out["approval_mode"] == "allowlist"
    assert out["approval_allowlist"] == ["git status"]
    disk = state.read_preferences(tmp_path)
    assert disk["approval_mode"] == "allowlist"
    assert disk["approval_allowlist"] == ["git status"]


def test_audit_respects_strict_grade(tmp_path):
    """Wire: strict grade → PermissionRequest never ACC-auto-allows."""
    import audit
    import state

    state.write_preferences(tmp_path, {"approval_mode": "strict"})
    out = audit.handle_payload(
        {"hook_event_name": "PermissionRequest", "tool_name": "Read", "tool_input": {}},
        tmp_path,
    )
    # No allow decision — leave normal Codex prompt (maybe systemMessage)
    decision = (out.get("hookSpecificOutput") or {}).get("decision") or {}
    assert decision.get("behavior") != "allow"


def test_audit_default_ask_still_auto_allows_read(tmp_path):
    import audit

    out = audit.handle_payload(
        {"hook_event_name": "PermissionRequest", "tool_name": "Read", "tool_input": {}},
        tmp_path,
    )
    assert out["hookSpecificOutput"]["decision"]["behavior"] == "allow"


def test_skill_yaml_registration():
    skill_dir = PLUGIN / "skills" / "approval-mode"
    skill_md = skill_dir / "SKILL.md"
    yaml_path = skill_dir / "agents" / "openai.yaml"
    assert skill_md.is_file()
    text = skill_md.read_text(encoding="utf-8")
    assert "name: approval-mode" in text
    assert text.startswith("---")
    assert 'description: "Use ' in text
    low = text.lower()
    assert "off" in low and "ask" in low and "allowlist" in low and "strict" in low
    assert "approval_grades.py" in text or "approval_grades" in text
    assert "codex" in low  # host boundary
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert data["interface"]["display_name"] == "ACC approval mode"
    policy = data.get("policy") or {}
    assert policy.get("allow_implicit_invocation") is False


def test_skill_budget_under_4000():
    text = (PLUGIN / "skills" / "approval-mode" / "SKILL.md").read_text(encoding="utf-8")
    assert len(text) <= 4000


def test_default_preferences_include_approval_mode():
    import state

    assert state.DEFAULT_PREFERENCES.get("approval_mode") == "ask"
    assert "approval_allowlist" in state.DEFAULT_PREFERENCES


def test_cli_json_roundtrip(tmp_path, capsys):
    code = ag.main(["--project-root", str(tmp_path), "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["grade"] == "ask"
    assert set(data["grades"]) == set(ag.GRADES)
