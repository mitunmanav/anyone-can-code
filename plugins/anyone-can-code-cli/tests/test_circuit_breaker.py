"""Backlog 5: same action failing twice must trip a loud circuit breaker.

Real trial evidence: "PromptScript global part failed again. ignore here" —
the agent repeated a failed action and shrugged. Also: a 40s health-check
timeout (exit 124) was pushed through as if the service had responded.
"""

from __future__ import annotations

import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(HOOKS))

import audit
import state


def _fail_payload(command: str) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_response": "error: install failed with exit status 1",
    }


def test_second_identical_failure_trips_breaker(tmp_path):
    first = audit.handle_payload(_fail_payload("npm install promptscript"), tmp_path)
    second = audit.handle_payload(_fail_payload("npm install promptscript"), tmp_path)

    ctx = (second.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "CIRCUIT BREAKER" in ctx, f"breaker did not trip: {ctx!r}"

    first_ctx = (first.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "CIRCUIT BREAKER" not in first_ctx, "breaker must not trip on first failure"


def test_breaker_writes_mistake_signal(tmp_path):
    audit.handle_payload(_fail_payload("npm install promptscript"), tmp_path)
    audit.handle_payload(_fail_payload("npm install promptscript"), tmp_path)

    signals = state.read_recent_jsonl(state.signal_log_path(tmp_path), limit=20)
    types = [s.get("signal_type") for s in signals]
    assert "repeated_failure" in types


def test_different_commands_do_not_trip(tmp_path):
    audit.handle_payload(_fail_payload("npm install left-pad"), tmp_path)
    result = audit.handle_payload(_fail_payload("npm install right-pad"), tmp_path)

    ctx = (result.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "CIRCUIT BREAKER" not in ctx


def test_exit_124_treated_as_service_not_ready(tmp_path):
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "curl http://127.0.0.1:8001/api/health"},
        "tool_response": "command timed out: exit code 124",
    }
    result = audit.handle_payload(payload, tmp_path)

    ctx = (result.get("hookSpecificOutput") or {}).get("additionalContext", "")
    assert "not ready" in ctx.lower(), f"exit 124 not flagged: {ctx!r}"
