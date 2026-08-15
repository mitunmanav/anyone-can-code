"""
Audit hook for PostToolUse and PermissionRequest.

Codex hooks docs (PermissionRequest): allow only when we decide; deny wins;
no decision → normal approval prompt. Exit 0 + empty = continue (so tool-gate
crashes must fail closed — see main()).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))


# Item 14: auto-allow only low-risk tools. Never blanket-allow Bash.
# (Audit: 35 yes/proceed clicks — kill spam, keep real risk prompts.)
SAFE_READ_TOOLS = (
    "Read",
    "Grep",
    "Glob",
    "LS",
    "Search",
    "WebSearch",
    "read_file",
    "list_dir",
    "grep",
)
# apply_patch / Edit / Write stay prompted unless already trusted by sandbox.
# Safe Bash = read-only or test commands only.
SAFE_BASH_PREFIXES = (
    "pytest",
    "python -m pytest",
    "python3 -m pytest",
    "npm test",
    "npm.cmd test",
    "npm run test",
    "npm.cmd run test",
    "git status",
    "git diff",
    "git log",
    "git branch",
    "ls ",
    "ls\n",
    "dir ",
    "dir\n",
    "rg ",
    "cat ",
    "type ",
    "echo ",
    "pwd",
    "whoami",
)

# Whole-command red flags: never auto-allow if any appear (Codex tool_input.command).
UNSAFE_AUTO_ALLOW_RE = re.compile(
    r"(?:"
    r"\|\s*(?:sudo\s+)?(?:bash|sh|zsh|dash|pwsh|powershell)\b"
    r"|(?:bash|sh|zsh|dash|pwsh|powershell)\s+<\("
    r"|(?:bash|sh|zsh)\s+-c\b"
    r"|\brm\s+(-[a-zA-Z]*f|--force)"
    r"|\bgit\s+push\b"
    r"|\bgit\s+reset\b"
    r"|\bcurl\b|\bwget\b|\biwr\b|\binvoke-webrequest\b"
    r"|\bformat\s+[cd]:"
    r"|\bdel\s+/s"
    r")",
    re.IGNORECASE,
)

# Split shell chains. Not full shell grammar; good enough for policy (docs: command string).
_SEGMENT_SPLIT_RE = re.compile(r"(?:&&|\|\||[;|\n])")


def split_command_segments(command: str) -> list[str]:
    text = str(command or "").strip()
    if not text:
        return []
    return [part.strip() for part in _SEGMENT_SPLIT_RE.split(text) if part.strip()]


def _segment_is_safe_prefix(segment: str) -> bool:
    first = segment.strip().lower()
    if not first:
        return False
    return any(first == p.strip() or first.startswith(p.strip()) for p in SAFE_BASH_PREFIXES)


def is_safe_auto_allow(tool_name: str, tool_input) -> bool:
    """True when PermissionRequest should auto-allow (kill approval spam).

    Codex docs: only return allow when every part is safe. Whole command chain
    must pass — not only the first segment before &&.
    """
    name = str(tool_name or "")
    if any(safe in name for safe in SAFE_READ_TOOLS):
        return True
    # apply_patch / Edit / Write: still need user for first trust — do not auto-allow
    if name in {"Bash", "bash", "Shell", "shell"} or name.endswith("Bash"):
        command = ""
        if isinstance(tool_input, dict):
            command = str(tool_input.get("command") or "")
        elif isinstance(tool_input, str):
            command = tool_input
        cmd = command.strip()
        if not cmd:
            return False
        if UNSAFE_AUTO_ALLOW_RE.search(cmd):
            return False
        segments = split_command_segments(cmd)
        if not segments:
            return False
        return all(_segment_is_safe_prefix(seg) for seg in segments)
    return False


def plain_approval_hint(tool_name: str, tool_input) -> str:
    """Plain words when we leave the normal approval prompt."""
    command = ""
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command") or tool_input.get("description") or "")[:120]
    return (
        f"ACC: Codex asks you because this step may change things "
        f"({tool_name}{': ' + command if command else ''}). "
        "Yes = allow once. No = stop."
    )


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
    tool_input = payload.get("tool_input", {})
    if is_safe_auto_allow(tool_name, tool_input):
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
    # Leave normal Codex prompt; add plain-words systemMessage (docs support it)
    print(
        json.dumps(
            {
                "systemMessage": plain_approval_hint(tool_name, tool_input),
            }
        )
    )


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


def extract_exit_code(tool_response, lower_response: str) -> int | None:
    """Best-effort exit code from PostToolUse tool_response (Codex: JSON value)."""
    if isinstance(tool_response, dict):
        for key in ("exit_code", "returncode", "exitCode", "status_code", "status"):
            if key not in tool_response:
                continue
            try:
                return int(tool_response[key])
            except (TypeError, ValueError):
                continue
    match = re.search(r"exit (?:code|status) (\d+)", lower_response or "", re.I)
    if match:
        return int(match.group(1))
    return None


def record_bash_result(repo_root: Path, payload: dict, lower_response: str) -> None:
    """Feed real Bash exit status into state.record_command_result (B11 repeat-failure guard)."""
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not command.strip():
        return
    extracted = extract_exit_code(payload.get("tool_response"), lower_response)
    if extracted is not None:
        exit_code = extracted
    else:
        exit_code = 1 if is_strong_failure_signal(lower_response) else 0
    state.record_command_result(repo_root, command, exit_code)


def maybe_auto_lint_context(repo_root: Path, payload: dict) -> str:
    """Soft PostToolUse hint when pref auto_lint=true and tool was an edit.

    Never raises into fail-closed. Never deny. Empty string = no inject.
    """
    try:
        import auto_lint as _auto_lint

        prefs = state.read_preferences(repo_root)
        if not _auto_lint.pref_enabled(prefs):
            return ""
        tool_name = str(payload.get("tool_name") or "")
        if not _auto_lint.is_edit_like_tool(tool_name):
            return ""
        tools = _auto_lint.detect_tools(repo_root)
        return _auto_lint.format_post_edit_hint(tools)
    except Exception:
        return ""


def handle_payload(payload: dict, repo_root: Path) -> dict:
    hook_event = payload.get("hook_event_name", "")
    if hook_event == "PostToolUse":
        log_tool_call(repo_root, payload)
        tool_name = payload.get("tool_name", "")
        tool_response = payload.get("tool_response", "")
        response_preview = summarize_response(tool_response)
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
        # Only silent-fail scan when exit looks successful (or unknown). Real nonzero = not silent.
        exit_code = extract_exit_code(tool_response, lower)
        if exit_code is None or exit_code == 0:
            import silent_failure_detector as _sfd  # lazy: only on success-looking exits

            scan = _sfd.scan_tool_response(
                {"output": response_preview, "exit_code": 0 if exit_code is None else exit_code}
            )
            if scan["silent_failures"]:
                detail = "; ".join(scan["silent_failures"])
                log_signal(repo_root, "silent_failure", f"{tool_name}: {detail}", payload)
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"Silent failure detected: {detail}",
                    }
                }
        # Opt-in soft hint only (pref auto_lint). Never deny / never fail-closed.
        auto_hint = maybe_auto_lint_context(repo_root, payload)
        if auto_hint:
            log_signal(repo_root, "auto_lint_hint", auto_hint[:200], payload)
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": auto_hint,
                }
            }
        return {}
    if hook_event == "PermissionRequest":
        log_tool_call(repo_root, payload)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        if is_safe_auto_allow(tool_name, tool_input):
            log_signal(repo_root, "permission_auto_allow", f"Allowed {tool_name}.", payload)
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": {"behavior": "allow"},
                }
            }
        return {"systemMessage": plain_approval_hint(tool_name, tool_input)}
    return {}


def _fail_closed_tool_gate(hook_event: str, reason: str) -> dict:
    """Codex: exit 0 empty continues. On gate crash, deny instead (docs deny shapes)."""
    if hook_event == "PermissionRequest":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "deny",
                    "message": reason,
                },
            }
        }
    if hook_event == "PreToolUse":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
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
        # Cannot parse event — fail closed for tool gates only if we know the name.
        print(json.dumps(_fail_closed_tool_gate("PermissionRequest", "ACC audit: bad hook JSON.")))
        sys.exit(2)
    except Exception as exc:  # pragma: no cover
        # Best effort: if stdin already consumed we may not have event name.
        print(
            json.dumps(
                _fail_closed_tool_gate(
                    "PermissionRequest",
                    f"ACC audit error ({type(exc).__name__}). Blocked for safety.",
                )
            ),
            file=sys.stdout,
        )
        print(f"ACC audit failed: {exc}", file=sys.stderr)
        sys.exit(2)
