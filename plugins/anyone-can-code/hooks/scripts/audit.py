"""
Audit hook for PostToolUse and PermissionRequest.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


SAFE_PERMISSION_TOOLS = ["Read", "Write", "Edit", "MultiEdit", "Bash"]


def find_repo_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return None


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


def main() -> None:
    payload = json.load(sys.stdin)
    repo_root = find_repo_root()
    if repo_root is None:
        print(json.dumps({}))
        return

    hook_event = payload.get("hook_event_name", "")
    if hook_event == "PostToolUse":
        log_tool_call(repo_root, payload)
        tool_name = payload.get("tool_name", "")
        response_preview = summarize_response(payload.get("tool_response", ""))
        log_signal(repo_root, "tool_used", f"{tool_name}: {response_preview}", payload)
        lower = response_preview.lower()
        if any(token in lower for token in ["error", "failed", "exception", "traceback"]):
            log_signal(repo_root, "verified_failure", f"{tool_name} looked bad.", payload)
        if any(token in lower for token in ["success", "passed", "ready", "\"stored\": true"]):
            log_signal(repo_root, "verified_success", f"{tool_name} looked good.", payload)
        print(json.dumps({}))
        return
    if hook_event == "PermissionRequest":
        handle_permission_request(payload, repo_root)
        return
    print(json.dumps({}))


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError:
        print(json.dumps({"systemMessage": "audit.py: invalid JSON on stdin."}))
    except Exception as exc:  # pragma: no cover - hook best effort
        print(json.dumps({"systemMessage": f"audit.py: {exc}"}))
