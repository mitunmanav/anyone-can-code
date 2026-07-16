"""
Small guard hook.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


GUARD_TAKEOVER_KEYS = {
    "workflow_owner", "workflow_state", "plan", "tracker",
    "commit_required", "approval_gate", "response_style", "route",
}


def check_workflow_takeover(payload: dict) -> dict:
    """Block any tool call that tries to set ACC-owned workflow control keys."""
    tool_input = payload.get("tool_input") or {}
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        command = tool_input

    for key in GUARD_TAKEOVER_KEYS:
        if f'"{key}"' in command or f"'{key}'" in command:
            return {
                "blocked": True,
                "reason": f"Foreign plugin tried to set ACC control key: {key}",
            }
    return {"blocked": False, "reason": ""}


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

DEPLOY_PATTERNS = [
    "vercel deploy",
    "netlify deploy",
    "heroku push",
    "railway up",
    "fly deploy",
    "git push",
]


def is_deploy_command(command: str) -> bool:
    cmd = command.lower()
    return any(p in cmd for p in DEPLOY_PATTERNS)


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


def detect_prompt_signals(payload: dict, repo_root: Path) -> list[tuple[str, str]]:
    prompt = (payload.get("prompt") or "").strip()
    lower = prompt.lower()
    signals: list[tuple[str, str]] = []

    # --- Verbatim repeat detection ---
    if prompt:
        prompt_log = state.prompt_log_path(repo_root)
        try:
            recent = state.read_recent_jsonl(prompt_log, limit=10)
            past_prompts = [r.get("prompt", "").strip() for r in recent]
            if prompt in past_prompts:
                preview = prompt[:80]
                signals.append(("repeated_prompt", f"verbatim repeat: {preview}"))
        except Exception:
            pass
        # Always log current prompt
        try:
            state.append_jsonl(
                prompt_log,
                {"timestamp": state.utc_now(), "prompt": prompt}
            )
        except Exception:
            pass

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


TURN_FIELD_MAX_CHARS = 240
MAX_TURN_CONTEXT_CHARS = 1200
TURN_LESSON_COUNT = 3


def _trim(text: str, limit: int = TURN_FIELD_MAX_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text.rfind(" ", 0, limit)
    if cut < limit // 2:
        cut = limit
    return text[:cut].rstrip() + "..."


def build_turn_context(prompt: str, repo_root: Path) -> str:
    """Per-turn anchor: comm rule + goal + next action + lessons.

    Codex drops skills from its menu when the skill list is full, but hooks
    always fire — so this injection is the one carrier that cannot vanish.

    Safety lines (rate-limit, interop, browser, host) are reserved and never
    truncated by the soft body budget.
    """
    preferences = state.read_preferences(repo_root)
    workflow = state.read_state(repo_root)
    uncertainty = state.classify_uncertainty(prompt)

    goal = workflow.get("active_goal") or workflow.get("active_task") or "Not set."
    next_action = workflow.get("next_action") or workflow.get("next_step") or "Not set."

    body_lines = [
        f"Comm rule: {preferences.get('communication_mode', 'caveman-strict')}. Talk short.",
        "Build rules: say assumptions before building. Simplest thing that works. "
        "Touch only what the task needs. Say how you will verify before you start.",
        f"Goal: {_trim(goal)}",
        f"Next action: {_trim(next_action)}",
    ]

    lessons = []
    try:
        recent = state.read_recent_jsonl(state.mistake_log_path(repo_root), limit=5)
        for entry in recent[-TURN_LESSON_COUNT:]:
            detail = entry.get("detail") or entry.get("summary") or entry.get("signal_type", "")
            if detail:
                lessons.append(f"- {_trim(detail, 120)}")
    except Exception:
        pass
    if lessons:
        body_lines.append("Lessons (do not repeat):")
        body_lines.extend(lessons)

    body_lines.append(f"Unclear: {uncertainty}.")

    try:
        import inbox as _inbox
        inbox_result = _inbox.process_prompt(prompt, repo_root)
        if inbox_result["context"]:
            body_lines.append(inbox_result["context"])
    except Exception:
        pass

    # Safety lines: reserved budget, never sliced off by body growth.
    safety_lines: list[str] = []
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import rate_limit_guard as _rate_limit_guard
        for line in _rate_limit_guard.build_guard_lines():
            if line:
                safety_lines.append(line)
    except Exception:
        pass

    interop_line = build_tool_interop_line(prompt)
    if interop_line:
        safety_lines.append(interop_line)

    browser_line = build_browser_policy_line(prompt)
    if browser_line:
        safety_lines.append(browser_line)

    host_line = build_host_detect_line()
    if host_line:
        safety_lines.append(host_line)

    return _join_body_and_safety(body_lines, safety_lines, MAX_TURN_CONTEXT_CHARS)


def _join_body_and_safety(
    body_lines: list[str],
    safety_lines: list[str],
    budget: int,
) -> str:
    """Join turn context so safety lines always fit inside budget."""
    safety = "\n".join(s for s in safety_lines if s).strip()
    body = "\n".join(body_lines).strip()
    if not safety:
        return body[:budget]
    # Reserve room for safety + separator newline.
    reserved = len(safety) + (1 if body else 0)
    if reserved >= budget:
        return safety[:budget]
    body_budget = budget - reserved
    if len(body) > body_budget:
        cut = body.rfind("\n", 0, body_budget)
        if cut < body_budget // 2:
            cut = body_budget
        body = body[:cut].rstrip()
    if body:
        return f"{body}\n{safety}"
    return safety


def build_browser_policy_line(prompt: str) -> str:
    """Safety: Chrome-first browser advice when the turn is about browsers/QA."""
    text = (prompt or "").lower()
    markers = (
        "browser",
        "chrome",
        "@browser",
        "@chrome",
        "visual qa",
        "screenshot",
        "click through",
    )
    if not any(m in text for m in markers):
        return ""
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import browser_policy as _browser_policy

        return _trim(_browser_policy.AGENT_RULE, 200)
    except Exception:
        return ""


def build_host_detect_line() -> str:
    """Host wording so CLI/Desktop claims stay honest."""
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import host_detect as _host_detect

        guide = _host_detect.host_guidance()
        host = guide.get("host") or "unknown"
        review = guide.get("review") or ""
        return _trim(f"Host: {host}. {review}", 160)
    except Exception:
        return ""


def build_tool_interop_line(prompt: str) -> str:
    """One compact OpenSpec-style interop line for the turn hook.

    Keeps Superpowers-style bindings visible even when skills menu is full.
    Never raises; empty string means no usable installed bindings.
    """
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import front_door as _front_door

        interop = _front_door.build_tool_interop(
            prompt,
            _front_door.scan_installed_plugins(),
            _front_door.ROUTES.get(
                _front_door.classify_entry_mode(prompt),
                ["plan", "execute", "verify"],
            ),
        )
        available = [
            item
            for item in (interop.get("bindings") or [])
            if item.get("available") and item.get("precheck") == "ok"
        ]
        if not available:
            return ""
        bits = []
        for item in available[:4]:
            skill = str(item.get("skill") or item.get("id") or "").strip()
            out = str((item.get("redirect") or {}).get("write_to") or "")
            leaf = out.rsplit("/", 1)[-1] if out else ""
            if skill and leaf:
                bits.append(f"{skill}→{leaf}")
            elif skill:
                bits.append(skill)
        if not bits:
            return ""
        return "Interop: " + "; ".join(bits) + ". ACC owns workflow + redirects."
    except Exception:
        return ""


def security_gate_for_deploy(repo_root: Path, command: str) -> str | None:
    """If deploy command, run production security scan. Plain reason or None.

    Fail closed: if the gate cannot run (import/scan error), return a block
    reason so deploy does not slip through silently.
    """
    if not is_deploy_command(command):
        return None
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import security_gate as _security_gate
        result = _security_gate.scan_project(repo_root)
    except Exception as exc:
        return (
            "Security gate could not run "
            f"({type(exc).__name__}). Fix the gate or project path before deploy."
        )
    if not isinstance(result, dict):
        return "Security gate returned no usable result. Block deploy until gate works."
    if result.get("ok"):
        return None
    lines = result.get("summary_lines") or [result.get("user_line") or "Security gate fail."]
    return " ".join(lines[:4])


def handle_payload(payload: dict, repo_root: Path) -> dict:
    hook_event = payload.get("hook_event_name", "")
    if hook_event == "UserPromptSubmit":
        prompt = payload.get("prompt", "")
        blocked_pattern = check_injection(prompt)
        if blocked_pattern:
            log_blocked(repo_root, payload, f"injection pattern: {blocked_pattern}")
            return {
                "decision": "block",
                "reason": f"Guard stop. Found '{blocked_pattern}'.",
            }

        for signal_type, detail in detect_prompt_signals(payload, repo_root):
            log_signal(repo_root, signal_type, detail, payload)
        context = build_turn_context(prompt, repo_root)
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }
    if hook_event == "PreToolUse":
        cmd = (payload.get("tool_input") or {}).get("command", "")
        deploy = is_deploy_command(cmd)

        # --- Hard DENY checks first. Warn must never preempt deny. ---
        if deploy:
            mock_db = os.environ.get("USE_MOCK_DB", "").strip().lower()
            if mock_db == "true":
                log_blocked(repo_root, payload, "deploy with USE_MOCK_DB=true")
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Guard blocked deploy: USE_MOCK_DB=true. "
                            "Set USE_MOCK_DB=false or remove it before deploying."
                        ),
                    }
                }
            gate_reason = security_gate_for_deploy(repo_root, cmd)
            if gate_reason:
                log_blocked(repo_root, payload, f"security gate: {gate_reason[:200]}")
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Security gate stop. Fix open signup / default password / "
                            f"secrets first. {gate_reason[:400]}"
                        ),
                    }
                }
        blocked = check_destructive_command(payload.get("tool_input", {}))
        if blocked:
            log_blocked(repo_root, payload, f"destructive command: {blocked}")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Guard stop bad command: {blocked}",
                }
            }

        # --- Advisory warn only if nothing denied above. ---
        if cmd and state.repeat_failure(repo_root, cmd):
            return {
                "systemMessage": "Same command failed twice. STOP. Change approach or ask user.",
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "Same command failed twice. STOP. Change approach or ask user."
                    ),
                },
            }

        # Safe to deploy — inject checklist
        if deploy:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "Pre-deploy checklist:\n"
                        "- USE_MOCK_DB not set (good)\n"
                        "- Confirm all required connectors built\n"
                        "- Confirm env vars set in target environment\n"
                        "- Run tests before deploy if not done\n"
                    ),
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
                "guard",
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
