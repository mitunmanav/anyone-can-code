"""
Small guard hook.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "new system prompt",
    "pretend you are",
    "system override",
    "forget everything",
]

DESTRUCTIVE_COMMANDS = [
    "rm -rf /",
    "rm -rf ~",
    "del /s /q",
    "format c:",
    "format d:",
    "git push --force",
    "git reset --hard",
]


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


def check_injection(text: str) -> str | None:
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            return pattern
    return None


def check_destructive_command(tool_input) -> str | None:
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        command = tool_input
    lower = command.lower().strip()
    for pattern in DESTRUCTIVE_COMMANDS:
        if lower.startswith(pattern) or pattern in lower:
            return pattern
    return None


def log_blocked(repo_root: Path, payload: dict, reason: str) -> None:
    entry = {
        "timestamp": state.utc_now(),
        "event": payload.get("hook_event_name"),
        "tool_name": payload.get("tool_name"),
        "reason": reason,
    }
    state.append_jsonl(state.journal_path(repo_root, "blocked-events.jsonl"), entry)


def log_signal(repo_root: Path, signal_type: str, detail: str, payload: dict) -> None:
    state.append_jsonl(
        state.signal_log_path(repo_root),
        {
            "timestamp": state.utc_now(),
            "signal_type": signal_type,
            "detail": detail[:200],
            "event": payload.get("hook_event_name"),
            "turn_id": payload.get("turn_id"),
        },
    )


def detect_prompt_signals(prompt: str) -> list[tuple[str, str]]:
    lower = prompt.lower()
    signals: list[tuple[str, str]] = []
    if "$learn" in lower or "/learn" in lower:
        signals.append(("manual_learn", "User want save learning."))
    if any(token in lower for token in ["not caveman", "follow caveman", "too long", "be brief", "strict caveman"]):
        signals.append(("style_correction", "User want caveman short talk."))
    if any(token in lower for token in ["wrong project", "wrong page", "wrong tool", "wrong context"]):
        signals.append(("wrong_context", "User say wrong project/page/tool/context."))
    if any(token in lower for token in ["you were wrong", "that is wrong", "mistake", "you slipped"]):
        signals.append(("user_correction", "User fix old wrong answer."))
    if any(token in lower for token in ["works", "good", "yes keep this", "this is right"]):
        signals.append(("accepted_result", "User say this path good."))
    return signals


def handle_user_prompt_submit(payload: dict, repo_root: Path) -> None:
    prompt = payload.get("prompt", "")
    blocked_pattern = check_injection(prompt)
    if blocked_pattern:
        log_blocked(repo_root, payload, f"injection pattern: {blocked_pattern}")
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": f"Guard stop. Found '{blocked_pattern}'.",
                }
            )
        )
        return

    phase, explicit_route = state.detect_phase(prompt)
    entry_mode = state.detect_entry_mode(prompt)
    uncertainty = state.classify_uncertainty(prompt)
    preferences = state.read_preferences(repo_root)

    current = state.write_state(
        repo_root,
        {
            "phase": phase or "route",
            "route": explicit_route or entry_mode,
            "entry_mode": entry_mode,
            "communication_mode": preferences.get("communication_mode", "normal"),
            "memory_mode": "mcp-first",
        },
    )

    for signal_type, detail in detect_prompt_signals(prompt):
        log_signal(repo_root, signal_type, detail, payload)

    context = (
        f"Talk: {current.get('communication_mode', 'caveman-strict')}. "
        f"Path: {entry_mode}/{current.get('phase', 'route')}. "
        f"Memory: {current.get('memory_mode', 'mcp-first')}. "
        f"Unclear: {uncertainty}. Talk short."
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }
        )
    )


def handle_pre_tool_use(payload: dict, repo_root: Path) -> None:
    blocked = check_destructive_command(payload.get("tool_input", {}))
    if blocked:
        log_blocked(repo_root, payload, f"destructive command: {blocked}")
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Guard stop bad command: {blocked}",
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
    if hook_event == "UserPromptSubmit":
        handle_user_prompt_submit(payload, repo_root)
        return
    if hook_event == "PreToolUse":
        handle_pre_tool_use(payload, repo_root)
        return
    print(json.dumps({}))


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError:
        print(json.dumps({"systemMessage": "guard.py: bad json in."}))
    except Exception as exc:  # pragma: no cover - hook best effort
        print(json.dumps({"systemMessage": f"guard.py: {exc}"}))
