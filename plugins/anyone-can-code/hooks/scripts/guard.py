"""
Small guard hook.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_core
import memory_promote
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
    "git push -f",
    "git reset --hard",
]

# Pipe / download-to-shell patterns (Codex PreToolUse sees tool_input.command).
# Broader than curl-only: cat|bash, echo|sh, bash -c "$(curl…)", process substitution.
PIPE_TO_SHELL_RE = re.compile(
    r"(?:"
    r"(?:curl|wget|iwr|invoke-webrequest|fetch|cat|type|echo|printf)\b[^\n]*\|\s*(?:sudo\s+)?"
    r"(?:bash|sh|zsh|dash|pwsh|powershell)\b"
    r"|\|\s*(?:sudo\s+)?(?:bash|sh|zsh|dash|pwsh|powershell)\b"
    r"|(?:bash|sh|zsh|dash|pwsh|powershell)\s+<\(\s*(?:curl|wget|iwr|fetch)\b"
    r"|(?:bash|sh|zsh|dash)\s+-c\b[^\n]*(?:curl|wget|iwr|fetch)\b"
    r")",
    re.IGNORECASE,
)

# Full production deploy / publish — run security gate. Plain git push is NOT this.
HARD_DEPLOY_PATTERNS = [
    "vercel deploy",
    "netlify deploy",
    "heroku push",
    "railway up",
    "fly deploy",
    "npm publish",
    "pnpm publish",
    "yarn publish",
    "twine upload",
    "gh release create",
    "git push --force",
    "git push -f",
]


def is_deploy_command(command: str) -> bool:
    """True for hard deploy/publish (security gate). Not every git push."""
    cmd = (command or "").lower()
    return any(p in cmd for p in HARD_DEPLOY_PATTERNS)


def is_git_push_command(command: str) -> bool:
    cmd = (command or "").lower()
    return "git push" in cmd


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
    if PIPE_TO_SHELL_RE.search(command):
        return "download piped to shell"
    return None


def log_blocked(repo_root: Path, payload: dict, reason: str) -> None:
    entry = {
        "timestamp": state.utc_now(),
        "event": payload.get("hook_event_name"),
        "tool_name": payload.get("tool_name"),
        "reason": reason,
    }
    state.append_jsonl(state.journal_path(repo_root, "blocked-events.jsonl"), entry)
    # ACC policy (not Codex API): durable safety receipt on every hard deny.
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import safety_receipts as _safety_receipts  # type: ignore

        tool_input = payload.get("tool_input") or {}
        cmd = ""
        if isinstance(tool_input, dict):
            cmd = str(tool_input.get("command") or "")
        elif isinstance(tool_input, str):
            cmd = tool_input
        prefs = state.read_preferences(repo_root)
        production_mode = bool(prefs.get("production_repo_caution"))
        _safety_receipts.write_action_receipt(
            repo_root,
            {
                "name": f"hook-block-{payload.get('tool_name') or 'tool'}",
                "type": "remote" if "push" in cmd.lower() or "deploy" in cmd.lower() else "delete",
                "command": cmd[:500],
                "production_mode": production_mode,
                "user_approval": "",
                "sandbox": "codex-native",
            },
            status="blocked",
            evidence=[
                f"hook:{payload.get('hook_event_name') or 'PreToolUse'}",
                f"reason:{reason[:240]}",
            ],
        )
    except Exception:
        pass  # journal line is enough if receipt write fails


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


def build_turn_context(
    prompt: str,
    repo_root: Path,
    *,
    session_id: str | None = None,
) -> str:
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
    # Token-burn scan is opt-in (ACC_TOKEN_BURN=1) — default off for speed.
    safety_lines: list[str] = []
    if os.environ.get("ACC_TOKEN_BURN", "").strip().lower() in {"1", "true", "yes"}:
        try:
            scripts = Path(__file__).resolve().parents[2] / "scripts"
            if str(scripts) not in sys.path:
                sys.path.insert(0, str(scripts))
            import rate_limit_guard as _rate_limit_guard
            for line in _rate_limit_guard.build_guard_lines(session_id=session_id):
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
    if os.environ.get("ACC_LOAD_LEAN", "").strip().lower() in {"1", "true", "yes"}:
        return ""
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
    """If hard deploy/publish, run production security scan. Plain reason or None.

    Fail closed: if the gate cannot run (import/scan error), return a block
    reason so deploy does not slip through silently.
    Plain git push does not run the full tree scan (slow / noisy).
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


def mark_turn_open(repo_root: Path, prompt: str) -> None:
    """Crash-resume anchor: if the app dies before Stop, SessionStart still
    knows what the user last asked for."""
    try:
        ask = memory_core.scrub((prompt or "").strip())[:200]
        state.write_state(repo_root, {"turn_status": "open", "open_ask": ask})
    except Exception:
        pass  # memory must never block the prompt


def _pretool_deny(reason: str) -> dict:
    """Codex PreToolUse deny shape (permissionDecision deny + reason)."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


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
        mark_turn_open(repo_root, prompt or "")
        try:
            for hit in memory_promote.detect_promotes(payload.get("prompt") or "", "prompt"):
                memory_promote.write_promote_note(repo_root, hit["kind"], hit["excerpt"])
        except Exception:
            pass  # capture is best effort; the prompt log already has the raw line
        context = build_turn_context(
            prompt,
            repo_root,
            session_id=str(payload.get("session_id") or "") or None,
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }
    if hook_event == "PreToolUse":
        tool_input = payload.get("tool_input") or {}
        cmd = ""
        if isinstance(tool_input, dict):
            cmd = tool_input.get("command", "") or ""
        elif isinstance(tool_input, str):
            cmd = tool_input
        deploy = is_deploy_command(cmd)

        # --- Hard DENY checks first. Warn must never preempt deny. ---
        takeover = check_workflow_takeover(payload)
        if takeover.get("blocked"):
            log_blocked(repo_root, payload, takeover.get("reason") or "workflow takeover")
            return _pretool_deny(
                f"Guard stop. {takeover.get('reason') or 'Foreign plugin tried ACC control keys.'}"
            )

        if deploy:
            mock_db = os.environ.get("USE_MOCK_DB", "").strip().lower()
            if mock_db == "true":
                log_blocked(repo_root, payload, "deploy with USE_MOCK_DB=true")
                return _pretool_deny(
                    "Guard blocked deploy: USE_MOCK_DB=true. "
                    "Set USE_MOCK_DB=false or remove it before deploying."
                )
            gate_reason = security_gate_for_deploy(repo_root, cmd)
            if gate_reason:
                log_blocked(repo_root, payload, f"security gate: {gate_reason[:200]}")
                return _pretool_deny(
                    "Security gate stop. Fix open signup / default password / "
                    f"secrets first. {gate_reason[:400]}"
                )
        blocked = check_destructive_command(tool_input)
        if blocked:
            log_blocked(repo_root, payload, f"destructive command: {blocked}")
            return _pretool_deny(f"Guard stop bad command: {blocked}")

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

        # Safe hard-deploy — inject checklist
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
        # Plain git push: short reminder only (not full security tree scan).
        if is_git_push_command(cmd) and "force" not in cmd.lower():
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "Git push: only if the user clearly asked. "
                        "No force-push. No half updates."
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
        # Codex: exit 0 empty continues the tool — fail closed for PreToolUse.
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "ACC guard: bad hook JSON. Blocked for safety.",
                    }
                }
            )
        )
        sys.exit(2)
    except Exception as exc:  # pragma: no cover
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"ACC guard error ({type(exc).__name__}). Blocked for safety."
                        ),
                    }
                }
            )
        )
        print(f"ACC guard failed: {exc}", file=sys.stderr)
        sys.exit(2)
