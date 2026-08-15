"""Detect + soft PostToolUse auto-lint (Aider-style after-edit check).

Docs first:
- Aider auto-lint after edits: https://aider.chat/docs/usage/lint-test.html
- Codex PostToolUse additionalContext: https://learn.chatgpt.com/docs/hooks
- Superpowers TDD + verify-before-done
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import audit  # noqa: E402
import auto_lint  # noqa: E402
import state  # noqa: E402


def test_detect_pytest_when_tests_dir(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    names = [t["name"] for t in auto_lint.detect_tools(tmp_path)]
    assert "pytest" in names


def test_detect_ruff_from_config(tmp_path: Path) -> None:
    (tmp_path / "ruff.toml").write_text("line-length = 100\n", encoding="utf-8")
    tools = auto_lint.detect_tools(tmp_path)
    assert any(t["name"] == "ruff" and "ruff" in t["command"] for t in tools)


def test_detect_eslint_from_package_and_config(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"devDependencies": {"eslint": "^9.0.0"}}),
        encoding="utf-8",
    )
    (tmp_path / "eslint.config.js").write_text("export default [];\n", encoding="utf-8")
    tools = auto_lint.detect_tools(tmp_path)
    assert any(t["name"] == "eslint" for t in tools)


def test_detect_empty_project(tmp_path: Path) -> None:
    assert auto_lint.detect_tools(tmp_path) == []


def test_detect_all_three(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff]\nline-length = 88\n[tool.pytest.ini_options]\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"devDependencies": {"eslint": "8.0.0"}}),
        encoding="utf-8",
    )
    (tmp_path / ".eslintrc.json").write_text("{}\n", encoding="utf-8")
    names = {t["name"] for t in auto_lint.detect_tools(tmp_path)}
    assert names == {"pytest", "ruff", "eslint"}


def test_format_hint_lists_commands(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "ruff.toml").write_text("", encoding="utf-8")
    tools = auto_lint.detect_tools(tmp_path)
    hint = auto_lint.format_post_edit_hint(tools)
    assert "AUTO-LINT" in hint
    assert "pytest" in hint.lower() or "python -m pytest" in hint
    assert "ruff" in hint
    assert "$auto-lint" in hint


def test_format_hint_empty_when_no_tools() -> None:
    assert auto_lint.format_post_edit_hint([]) == ""


def test_cli_json(tmp_path: Path, capsys) -> None:
    (tmp_path / "tests").mkdir()
    code = auto_lint.main(["--json", "--root", str(tmp_path)])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert any(row["name"] == "pytest" for row in data)


def test_pref_off_no_posttooluse_hint(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    state.write_preferences(tmp_path, {"auto_lint": False})
    result = audit.handle_payload(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"patch": "ok"},
            "tool_response": "ok",
        },
        tmp_path,
    )
    ctx = (result.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "AUTO-LINT" not in ctx


def test_pref_on_edit_tool_soft_hint(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "ruff.toml").write_text("", encoding="utf-8")
    state.write_preferences(tmp_path, {"auto_lint": True})
    result = audit.handle_payload(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"patch": "diff"},
            "tool_response": "success",
        },
        tmp_path,
    )
    hso = result.get("hookSpecificOutput") or {}
    assert hso.get("hookEventName") == "PostToolUse"
    ctx = hso.get("additionalContext", "")
    assert "AUTO-LINT" in ctx
    # Soft only — never a deny decision
    assert "permissionDecision" not in hso
    assert "decision" not in hso


def test_pref_on_bash_no_hint(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    state.write_preferences(tmp_path, {"auto_lint": True})
    result = audit.handle_payload(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hi"},
            "tool_response": "hi\nexit code 0",
        },
        tmp_path,
    )
    ctx = (result.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "AUTO-LINT" not in ctx


def test_strong_failure_wins_over_auto_lint(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    state.write_preferences(tmp_path, {"auto_lint": True})
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"patch": "x"},
        "tool_response": "Traceback (most recent call last):\n  File x\nError",
    }
    # First failure → no breaker yet; second trips breaker
    audit.handle_payload(payload, tmp_path)
    second = audit.handle_payload(payload, tmp_path)
    ctx = (second.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "CIRCUIT BREAKER" in ctx
    # Breaker path must not be replaced by soft lint spam alone
    assert ctx.startswith("CIRCUIT BREAKER") or "CIRCUIT BREAKER" in ctx


def test_auto_lint_never_fail_closed_deny(tmp_path: Path) -> None:
    """auto_lint path must not produce PermissionRequest/PreToolUse deny shapes."""
    (tmp_path / "tests").mkdir()
    state.write_preferences(tmp_path, {"auto_lint": True})
    result = audit.handle_payload(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"path": "a.py", "content": "x=1"},
            "tool_response": "wrote",
        },
        tmp_path,
    )
    hso = result.get("hookSpecificOutput") or {}
    assert hso.get("permissionDecision") != "deny"
    decision = hso.get("decision") or {}
    assert decision.get("behavior") != "deny"


def test_skill_frontmatter_and_display_name() -> None:
    skill_md = (PLUGIN / "skills" / "auto-lint" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: auto-lint" in skill_md
    assert "auto_lint.py" in skill_md
    yaml_text = (PLUGIN / "skills" / "auto-lint" / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    assert 'display_name: "ACC auto lint"' in yaml_text
    assert "allow_implicit_invocation: false" in yaml_text


def test_skill_under_budget() -> None:
    size = len((PLUGIN / "skills" / "auto-lint" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
