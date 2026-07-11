"""Tests for guard.py — prompt signal detection."""
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))

import guard
import state


def test_verbatim_repeat_detected(tmp_path):
    """Guard must signal repeated_prompt when user sends same message twice."""
    prompt = "what is the status of the project"

    # Simulate first occurrence in log
    state.append_jsonl(
        state.prompt_log_path(tmp_path),
        {"timestamp": "2026-06-24T09:00:00Z", "prompt": prompt}
    )

    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
    }
    signals = guard.detect_prompt_signals(payload, tmp_path)
    signal_types = [s[0] for s in signals]
    assert "repeated_prompt" in signal_types


def test_deploy_blocked_when_mock_db_set(tmp_path, monkeypatch):
    """PreToolUse must deny vercel deploy when USE_MOCK_DB=true."""
    monkeypatch.setenv("USE_MOCK_DB", "true")
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "vercel deploy --prod"},
    }
    result = guard.handle_payload(payload, tmp_path)
    hook_out = result.get("hookSpecificOutput", {})
    assert hook_out.get("permissionDecision") == "deny"
    assert "USE_MOCK_DB" in hook_out.get("permissionDecisionReason", "")


def test_deploy_checklist_injected_when_safe(tmp_path, monkeypatch):
    """PreToolUse must inject pre-deploy checklist when mock DB not set."""
    monkeypatch.delenv("USE_MOCK_DB", raising=False)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "vercel deploy --prod"},
    }
    result = guard.handle_payload(payload, tmp_path)
    hook_out = result.get("hookSpecificOutput", {})
    # Should NOT be denied, but should inject checklist context
    assert hook_out.get("permissionDecision") != "deny"
    ctx = hook_out.get("additionalContext", "")
    assert "checklist" in ctx.lower() or "deploy" in ctx.lower()


def test_git_push_blocked_when_mock_db_set(tmp_path, monkeypatch):
    """git push must be treated as a deploy command and blocked when USE_MOCK_DB=true."""
    monkeypatch.setenv("USE_MOCK_DB", "true")
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin main"},
    }
    result = guard.handle_payload(payload, tmp_path)
    hook_out = result.get("hookSpecificOutput", {})
    assert hook_out.get("permissionDecision") == "deny"
    assert "USE_MOCK_DB" in hook_out.get("permissionDecisionReason", "")


def test_turn_context_injects_all_anchor_blocks(tmp_path):
    """Backlog 2: every turn carries comm rule + goal + next action + lessons.

    Codex omits skills when the skill list is full (proven in real trial),
    so the per-turn hook is the only reliable carrier for these anchors.
    """
    state.write_state(tmp_path, {
        "active_goal": "Build todo app",
        "next_action": "Write tests for login",
    })
    state.append_jsonl(
        state.mistake_log_path(tmp_path),
        {"timestamp": "2026-07-06T10:00:00Z", "detail": "Never deploy with mock DB"},
    )

    payload = {"hook_event_name": "UserPromptSubmit", "prompt": "what next?"}
    result = guard.handle_payload(payload, tmp_path)

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "caveman" in ctx, "comm rule missing"
    assert "Build todo app" in ctx, "active goal missing"
    assert "Write tests for login" in ctx, "next action missing"
    assert "Never deploy with mock DB" in ctx, "lesson missing"


def test_turn_context_trims_long_goal(tmp_path):
    """Injection must stay small: long goals are trimmed, not dumped."""
    state.write_state(tmp_path, {"active_goal": "x" * 1000})

    payload = {"hook_event_name": "UserPromptSubmit", "prompt": "hi"}
    result = guard.handle_payload(payload, tmp_path)

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert len(ctx) < 1000, f"context too big: {len(ctx)} chars"
