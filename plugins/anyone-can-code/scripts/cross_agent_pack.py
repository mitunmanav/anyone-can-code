#!/usr/bin/env python3
"""Phase E — cross-agent pickup, env adapt, model switch, headless, GH review, proof.

Wrap native Codex only. No RTK. No rebuild of model picker or GitHub review bot.
Explain → suggest → user decides. Label [CHEAP]/[HUNGRY].
"""

from __future__ import annotations

import os
import platform
import shlex
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cost_labels
except Exception:  # pragma: no cover
    cost_labels = None  # type: ignore


def _tag(kind: str, text: str) -> str:
    if cost_labels is not None:
        return cost_labels.tag_line(text, kind)
    tag = "[CHEAP]" if kind == "cheap" else "[HUNGRY]"
    return f"{tag} {text}"


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


# --- 28: env adapt (fix "rtk on Windows") ---

def detect_env(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Detect OS/shell for command rules. Never assume Unix or rtk."""
    context = context or {}
    os_hint = _norm(context.get("os") or context.get("platform"))
    shell_hint = _norm(context.get("shell"))

    if os_hint:
        windows = "windows" in os_hint or os_hint in {"win32", "nt"}
    elif shell_hint in {"powershell", "pwsh", "cmd", "cmd.exe"}:
        windows = True
    else:
        windows = os.name == "nt" or sys.platform == "win32"

    if shell_hint in {"powershell", "pwsh"}:
        shell = "powershell"
    elif shell_hint in {"cmd", "cmd.exe"}:
        shell = "cmd"
    elif shell_hint in {"bash", "sh", "zsh", "fish"}:
        shell = "posix"
    else:
        shell = "powershell" if windows else "posix"

    package_runner = "npm.cmd" if windows and shell in {"powershell", "cmd"} else "npm"
    return {
        "os": "windows" if windows else (os_hint or platform.system().lower() or "linux"),
        "windows": windows,
        "shell": shell,
        "path_sep": "\\" if windows else "/",
        "package_runner": package_runner,
        "python": "python" if windows else "python3",
        "forbid_rtk": True,
        "host": "codex",
    }


def env_agent_line(env: dict[str, Any] | None = None) -> str:
    env = env or detect_env()
    if env["windows"]:
        return (
            f"Env: Windows / {env['shell']}. Use {env['package_runner']}, not bare npm. "
            f"No Bash-only ||. Paths use {env['path_sep']}. "
            "Adapt to this machine — no Unix-only assumptions. No rtk (not Codex)."
        )
    return (
        f"Env: {env['os']} / {env['shell']}. Use {env['package_runner']}. "
        f"Paths use {env['path_sep']}. Adapt to this machine. No rtk (not Codex)."
    )


def env_howto() -> dict[str, Any]:
    env = detect_env()
    return {
        "id": "env_adapt",
        "native": "SessionStart + host OS/shell",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "ACC adapts to your computer (Windows/Mac/Linux) at start. "
            "It will not force Linux-only tricks. You choose tools.",
        ),
        "agent_line": env_agent_line(env),
        "env": env,
    }


# --- 28: cross-agent pickup ---

def pickup_howto() -> dict[str, Any]:
    return {
        "id": "pickup",
        "native": "ACC handoff + $resume + bridge (create_thread)",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Picking up work from another chat or agent? Say 'continue' or 'handoff'. "
            "ACC loads goal, next step, git, memory. You decide. Nothing forced.",
        ),
        "agent_line": (
            "Pickup: run build_handoff or $resume. Same project local. "
            "create_thread with full prompt — no fork_thread unless user says fork. "
            "Bridge only for installed plugins. Never auto-delegate."
        ),
    }


# --- 29: model switch via new chat + handoff ---

def model_switch_howto() -> dict[str, Any]:
    return {
        "id": "model_switch",
        "native": "Desktop model control / CLI /model + create_thread handoff",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Want a different model? Small change: use the model menu under the chat. "
            "Big switch mid-work: new chat + handoff so context and model stay clear. You choose.",
        ),
        "agent_line": (
            "Do not invent a model-switch API. Small: native UI /model. "
            "Big: build_handoff --model --reasoning + create_thread. User decides."
        ),
    }


def format_model_switch_prompt(
    *,
    goal: str,
    model: str,
    reasoning: str = "medium",
    next_action: str = "",
    project_root: str = ".",
) -> str:
    env = detect_env()
    next_bit = (next_action or "(continue from goal)").strip()
    return (
        "Continue work in this same local project. Do not fork.\n\n"
        "Communication:\n"
        "- strict caveman style: short, direct, simple. Technical terms exact.\n"
        "- user is non-technical. Explain outcomes plainly.\n"
        "- ACC orchestrator stays workflow owner.\n\n"
        f"Target model: {model.strip()} (reasoning={reasoning.strip() or 'medium'})\n"
        f"Project root: {project_root}\n"
        f"Active goal: {goal.strip() or 'project status'}\n"
        f"Next action: {next_bit}\n"
        f"Environment: {env['os']} / {env['shell']}; package={env['package_runner']}\n"
        "Rules: verify before done. No push/PR/release without explicit user command.\n"
        "No rtk. Adapt shell to this machine.\n"
    )


# --- 30: headless ---

def headless_howto() -> dict[str, Any]:
    return {
        "id": "headless",
        "native": "codex exec (non-interactive)",
        "cost": "hungry",
        "user_line": _tag(
            "hungry",
            "Need Codex without the chat UI (scripts/CI)? Use headless: codex exec \"task\". "
            "Default is safe read-only. Wider access only if you say so. You decide.",
        ),
        "agent_line": (
            "Wrap codex exec. Default sandbox read-only. "
            "workspace-write only when user needs edits. Never force danger-full-access. "
            "Prefer --json or -o for machine output. GitHub Action for GH CI."
        ),
    }


def format_headless_command(
    prompt: str,
    *,
    sandbox: str = "read-only",
    json_out: bool = False,
    output_file: str | None = None,
    ephemeral: bool = False,
) -> str:
    parts = ["codex exec"]
    sb = (sandbox or "read-only").strip()
    if sb and sb != "read-only":
        parts.extend(["--sandbox", sb])
    if json_out:
        parts.append("--json")
    if ephemeral:
        parts.append("--ephemeral")
    if output_file:
        parts.extend(["-o", output_file])
    parts.append(shlex.quote((prompt or "summarize this repo").strip()))
    return " ".join(parts)


# --- 31: GitHub auto-review ---

def github_review_howto() -> dict[str, Any]:
    return {
        "id": "github_review",
        "native": "Codex code review in GitHub (+ optional openai/codex-action)",
        "cost": "hungry",
        "force": False,
        "user_line": _tag(
            "hungry",
            "Want auto review on pull requests? Need Codex cloud on the repo, then "
            "chatgpt.com/codex/settings/code-review → turn on Code review. "
            "Auto: Automatic reviews. One-shot: comment @codex review. You choose. Nothing forced.",
        ),
        "agent_line": (
            "Wrap native GitHub code review. Do not rebuild a review bot. "
            "Explain cloud + settings path. Optional CI: openai/codex-action. User decides."
        ),
        "setup_steps": [
            "Set up Codex cloud for the repository",
            "Open https://chatgpt.com/codex/settings/code-review",
            "Turn on Code review for the repo",
            "Optional: turn on Automatic reviews",
            "Or comment @codex review on a pull request",
            "Optional AGENTS.md Review guidelines for repo rules",
        ],
    }


# --- 32: no done without proof ---

FAKE_DONE_PHRASES = (
    "all done",
    "it works",
    "works perfectly",
    "works perfectly.",
    "ship it",
    "fully fixed",
    "completely fixed",
    "perfect",
    "we're done",
    "finished and verified",
)

# Minimum evidence keys by claim kind
PROOF_REQUIRED = {
    "micro": ("tests",),
    "bug": ("tests",),
    "feature": ("tests",),
    "product": ("tests", "interaction"),
    "ship": ("tests", "review", "user_yes"),
    "general": ("tests",),
}


def claim_done(
    evidence: dict[str, Any] | None,
    *,
    kind: str = "general",
) -> dict[str, Any]:
    """Allow 'done' only when required proof fields are non-empty."""
    evidence = evidence or {}
    key = (kind or "general").strip().lower()
    required = PROOF_REQUIRED.get(key, PROOF_REQUIRED["general"])
    missing: list[str] = []
    present: dict[str, str] = {}
    for field in required:
        val = str(evidence.get(field) or "").strip()
        if not val:
            if field == "interaction":
                missing.append("real-use proof (user path / interaction), not unit tests alone")
            elif field == "review":
                missing.append("review pane or GitHub review seen")
            elif field == "user_yes":
                missing.append("user said yes in plain words")
            else:
                missing.append(f"{field} evidence")
        else:
            present[field] = val[:200]
    ok = not missing
    if ok:
        user_line = (
            "Proof OK for this claim. "
            + "; ".join(f"{k}: {v}" for k, v in present.items())
            + ". Still name what was not checked."
        )
    else:
        user_line = (
            "Not done yet — missing proof: "
            + "; ".join(missing)
            + ". Run checks, then claim done."
        )
    return {
        "ok": ok,
        "kind": key,
        "required": list(required),
        "missing": missing,
        "present": present,
        "user_line": user_line,
        "agent_line": (
            "Never claim done/works/perfect without named evidence. "
            "Built ≠ verified. Unit tests alone ≠ product done."
        ),
        "force": False,
    }


def scan_done_claims(text: str) -> list[str]:
    """Flag casual done language that needs proof (cheap text scan)."""
    low = (text or "").lower()
    flags: list[str] = []
    for phrase in FAKE_DONE_PHRASES:
        if phrase in low:
            flags.append(f"risky phrase: '{phrase}' — need proof before saying done")
    if "done" in low and "proof" not in low and "checked" not in low:
        if any(w in low for w in ("all done", "we're done", "is done", "task done")):
            if not any(f.startswith("risky phrase: 'all done") for f in flags):
                flags.append("said done without naming proof")
    return flags


def proof_gate_howto() -> dict[str, Any]:
    return {
        "id": "proof_gate",
        "native": "ACC $verify + claim_done",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "ACC will not say 'done' until it shows proof (tests, real try, or your ok). "
            "You always see what was checked.",
        ),
        "agent_line": claim_done({})["agent_line"],
    }


# --- menu ---

def all_features() -> list[dict[str, Any]]:
    return [
        env_howto(),
        pickup_howto(),
        model_switch_howto(),
        headless_howto(),
        github_review_howto(),
        proof_gate_howto(),
    ]


def plain_menu() -> str:
    lines = ["Cross-agent + model tools (native wrap). You choose:"]
    for f in all_features():
        lines.append(f"- {f['id']}: {f['user_line']}")
    lines.append("Nothing forced. Big model swap → new chat + handoff. Done needs proof.")
    return "\n".join(lines)


def suggest_for_request(request: str) -> list[str]:
    low = (request or "").lower()
    out: list[str] = []
    if any(w in low for w in ("continue", "pickup", "pick up", "other agent", "other chat", "handoff")):
        out.append(pickup_howto()["user_line"])
    if any(w in low for w in ("switch model", "change model", "different model", "/model")):
        out.append(model_switch_howto()["user_line"])
    if any(w in low for w in ("headless", "codex exec", "ci", "no ui", "script")):
        out.append(headless_howto()["user_line"])
    if any(w in low for w in ("github review", "pr review", "auto review", "@codex")):
        out.append(github_review_howto()["user_line"])
    if any(w in low for w in ("done", "finished", "works", "ship")):
        out.append(proof_gate_howto()["user_line"])
    if not out:
        out.append(_tag("cheap", "Continue work: handoff/resume. Model: menu or new chat. Done needs proof."))
    seen: set[str] = set()
    uniq: list[str] = []
    for line in out:
        if line not in seen:
            seen.add(line)
            uniq.append(line)
    return uniq
