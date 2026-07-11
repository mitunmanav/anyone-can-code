"""
Audit hook for PostToolUse and PermissionRequest.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import silent_failure_detector


SAFE_PERMISSION_TOOLS = ["Read", "Write", "Edit", "MultiEdit", "Bash"]


def log_tool_call(repo_root: Path, payload: dict) -> None:
    preview = ""
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict):
        preview = tool_input.get("command", "")[:240]
    elif isinstance(tool_input, str):
        preview = tool_input[:240]

    entry = {
        "timestamp": state.utc_now(),
        "hook_event": payload.get("hook_event_name"),
        "tool_name": payload.get("tool_name"),
        "tool_use_id": payload.get("tool_use_id"),
        "command_preview": preview,
        "session_id": payload.get("session_id"),
    }
    state.append_jsonl(state.journal_path(repo_root, "tool-usage.jsonl"), entry)


def log_signal(repo_root: Path, signal_type: str, detail: str, payload: dict) -> None:
    state.append_jsonl(
        state.signal_log_path(repo_root),
        {
            "timestamp": state.utc_now(),
            "signal_type": signal_type,
            "detail": detail[:200],
            "event": payload.get("hook_event_name"),
            "tool_name": payload.get("tool_name"),
            "turn_id": payload.get("turn_id"),
        },
    )


def summarize_response(tool_response) -> str:
    if isinstance(tool_response, str):
        return tool_response[:240]
    try:
        return json.dumps(tool_response)[:240]
    except TypeError:
        return str(tool_response)[:240]


def handle_permission_request(payload: dict, repo_root: Path) -> None:
    log_tool_call(repo_root, payload)
    tool_name = payload.get("tool_name", "")
    if any(allowed in tool_name for allowed in SAFE_PERMISSION_TOOLS):
        log_signal(repo_root, "permission_auto_allow", f"Allowed {tool_name}.", payload)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PermissionRequest",
                        "decision": {"behavior": "allow"},
                    }
                }
            )
        )
        return
    print(json.dumps({}))


FAILURE_LEDGER = "failure-ledger.jsonl"
FAILURE_LOOKBACK = 20

# Important-3 / Minor-7: single strong-signal pattern, used everywhere a
# response is checked for real failure. Plain "error"/"failed"/"exception"/
# "traceback" text ALONE is not enough (e.g. `grep error log.txt` output) --
# that caused false "failed twice. STOP." warnings. Only a real nonzero
# exit code phrase or an actual Python traceback header counts. "exit code
# 124" / "exit status 124" (the existing timeout convention) still matches
# because 124 starts with a nonzero digit.
STRONG_FAILURE_PATTERN = re.compile(
    r"exit (code|status) [1-9]\d*|traceback \(most recent call last\)",
    re.IGNORECASE,
)


def is_strong_failure_signal(lower_response: str) -> bool:
    """True only for strong failure signals; plain error words don't count."""
    return bool(STRONG_FAILURE_PATTERN.search(lower_response))


def _command_signature(payload: dict) -> str:
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else str(tool_input)
    return f"{payload.get('tool_name', '')}::{command.strip()[:200]}"


def check_repeated_failure(repo_root: Path, payload: dict) -> str:
    """Record this failure; return breaker context if the same action failed before."""
    signature = _command_signature(payload)
    ledger = state.journal_path(repo_root, FAILURE_LEDGER)
    previous = state.read_recent_jsonl(ledger, limit=FAILURE_LOOKBACK)
    state.append_jsonl(ledger, {"timestamp": state.utc_now(), "signature": signature})
    if not any(row.get("signature") == signature for row in previous):
        return ""
    log_signal(repo_root, "repeated_failure", f"Repeated failure: {signature}", payload)
    return (
        "CIRCUIT BREAKER: this exact action already failed before. "
        "STOP. Do not run it again. Change the approach or tell the user what is blocked."
    )


def record_bash_result(repo_root: Path, payload: dict, lower_response: str) -> None:
    """Feed real Bash exit status into state.record_command_result (B11 repeat-failure guard)."""
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not command.strip():
        return
    exit_code = 1 if is_strong_failure_signal(lower_response) else 0
    state.record_command_result(repo_root, command, exit_code)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    hook_event = payload.get("hook_event_name", "")
    if hook_event == "PostToolUse":
        log_tool_call(repo_root, payload)
        tool_name = payload.get("tool_name", "")
        response_preview = summarize_response(payload.get("tool_response", ""))
        log_signal(repo_root, "tool_used", f"{tool_name}: {response_preview}", payload)
        lower = response_preview.lower()
        if tool_name == "Bash":
            record_bash_result(repo_root, payload, lower)
        if "exit code 124" in lower or "exit status 124" in lower:
            log_signal(repo_root, "verified_failure", f"{tool_name} timed out (124).", payload)
            return {"hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "Exit 124 = timeout. The service is NOT ready. "
                    "Do not treat this as success; wait or fix startup first."
                ),
            }}
        if is_strong_failure_signal(lower):
            log_signal(repo_root, "verified_failure", f"{tool_name} looked bad.", payload)
            breaker = check_repeated_failure(repo_root, payload)
            if breaker:
                return {"hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": breaker,
                }}
        if any(token in lower for token in ["success", "passed", "ready", "\"stored\": true"]):
            log_signal(repo_root, "verified_success", f"{tool_name} looked good.", payload)
        scan = silent_failure_detector.scan_tool_response({"output": response_preview, "exit_code": 0})
        if scan["silent_failures"]:
            detail = "; ".join(scan["silent_failures"])
            log_signal(repo_root, "silent_failure", f"{tool_name}: {detail}", payload)
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                          "additionalContext": f"Silent failure detected: {detail}"}}
        return {}
    if hook_event == "PermissionRequest":
        log_tool_call(repo_root, payload)
        tool_name = payload.get("tool_name", "")
        if any(allowed in tool_name for allowed in SAFE_PERMISSION_TOOLS):
            log_signal(repo_root, "permission_auto_allow", f"Allowed {tool_name}.", payload)
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": {"behavior": "allow"},
                }
            }
    return {}


def main() -> None:
    payload = json.load(sys.stdin)
    resolution = state.resolve_hook_project(payload)
    print(
        json.dumps(
            state.run_hook_attempt(
                resolution,
                "audit",
                payload,
                lambda: handle_payload(payload, Path(resolution["project_root"])),
            )
        )
    )


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError:
        print(json.dumps({}))
    except Exception as exc:  # pragma: no cover - hook best effort
        print(json.dumps({}))
