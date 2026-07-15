#!/usr/bin/env python3
"""Phase D walk-away pack — wrap native Codex powers in plain words.

Never rebuild /goal, notifications, cloud, review pane, or Sites.
Explain → suggest → user decides. Label [CHEAP]/[HUNGRY].
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import security_gate
except Exception:  # pragma: no cover
    security_gate = None  # type: ignore

try:
    import cost_labels
except Exception:  # pragma: no cover
    cost_labels = None  # type: ignore


def _tag(kind: str, text: str) -> str:
    if cost_labels is not None:
        return cost_labels.tag_line(text, kind)
    tag = "[CHEAP]" if kind == "cheap" else "[HUNGRY]"
    return f"{tag} {text}"


# --- 20: /goal ---

def goal_howto() -> dict[str, Any]:
    return {
        "id": "goal",
        "native": "/goal in Codex Desktop / CLI / IDE",
        "cost": "hungry",
        "user_line": _tag(
            "hungry",
            "Long job? Type /goal with: what done looks like, limits, and how to check. "
            "You can pause/resume in the progress row. Walk away; come back later.",
        ),
        "agent_line": (
            "Wrap native /goal. Do not rebuild a goal engine. "
            "Include outcome + constraints + verification. User decides to start."
        ),
        "template": (
            "Outcome: {outcome}\n"
            "Constraints: {constraints}\n"
            "Done when: {verification}\n"
        ),
    }


def format_goal_prompt(
    outcome: str,
    constraints: str = "Stay in this project. No force-push. No secrets.",
    verification: str = "Tests pass and user can try the main path.",
) -> str:
    return (
        f"Outcome: {outcome.strip()}\n"
        f"Constraints: {constraints.strip()}\n"
        f"Done when: {verification.strip()}\n"
    )


# --- 21: notifications ---

def notifications_howto() -> dict[str, Any]:
    return {
        "id": "notifications",
        "native": "Codex Settings notifications + optional user notify= script",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Want pings when work needs you? Codex Settings → turn on notifications "
            "(desktop). For phone/Slack later: user-level notify script can call a webhook. "
            "You choose. Nothing forced.",
        ),
        "agent_line": (
            "Wrap native notifications. Do not build a new push service. "
            "Desktop first. Webhook/Slack only if user asks and sets notify in ~/.codex/config.toml."
        ),
        "setup_steps": [
            "Open Codex Settings → Notifications",
            "Allow OS permission if asked",
            "Optional later: set notify = [\"python3\", \"path/to/webhook.py\"] in user config",
        ],
    }


# --- 22: cloud ---

def cloud_howto() -> dict[str, Any]:
    return {
        "id": "cloud",
        "native": "Codex Cloud / remote thread",
        "cost": "hungry",
        "user_line": _tag(
            "hungry",
            "Long job and you need the laptop free? Cloud can run remote in the background. "
            "Needs GitHub connected. Local stays if no GitHub. You decide.",
        ),
        "agent_line": (
            "Suggest Cloud only for long/big work. Explain GitHub need. "
            "Never force. If no GitHub, stay Local."
        ),
        "requires": ["github_connected"],
    }


def should_suggest_cloud(task_text: str) -> bool:
    low = (task_text or "").lower()
    markers = (
        "long",
        "overnight",
        "big refactor",
        "migrate whole",
        "walk away",
        "while i sleep",
        "background",
        "hours",
    )
    return any(m in low for m in markers)


# --- 23: robot walkthrough (plain progress) ---

def walkthrough_line(step: str, phase: str = "doing") -> str:
    """One plain line for progress. No jargon. No file paths."""
    name = " ".join(str(step or "this step").split())[:80]
    p = (phase or "doing").strip().lower()
    if p in {"start", "doing", "now"}:
        return f"Making {name} now."
    if p in {"done", "ok", "pass"}:
        return f"Done: {name}."
    if p in {"fail", "error", "blocked"}:
        return f"Stuck on {name}. Trying a different way or will ask you."
    if p in {"next", "then"}:
        return f"Next: {name}."
    if p in {"check", "verify"}:
        return f"Checking {name}."
    return f"{name}."


def walkthrough_block(steps: list[dict[str, str]]) -> str:
    """steps: [{step, phase}] → plain multi-line progress."""
    lines = [walkthrough_line(s.get("step", ""), s.get("phase", "doing")) for s in steps]
    return "\n".join(lines)


# --- 24: review gate before ship ---

def review_gate_howto() -> dict[str, Any]:
    return {
        "id": "review_gate",
        "native": "Codex review pane + /review",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Before anything goes live: open the review pane (green=added, red=removed). "
            "You can revert any file. Then security check. Then you say ship.",
        ),
        "agent_line": (
            "Never claim shipped without review pane handoff + security gate + explicit user yes."
        ),
    }


def ship_gate(repo_root: Path | None = None) -> dict[str, Any]:
    """Hard checklist before deploy. User still decides."""
    findings: list[str] = []
    security_ok = True
    if repo_root is not None and security_gate is not None:
        result = security_gate.scan_project(Path(repo_root))
        security_ok = bool(result.get("ok"))
        if not security_ok:
            findings.extend(result.get("summary_lines") or [result.get("user_line", "security fail")])
    checks = [
        {"id": "review_pane", "plain": "User saw review pane (green/red) or said skip review", "required": True},
        {"id": "security", "plain": "Security gate PASS (no open signup / default password / fake secrets)", "required": True},
        {"id": "user_yes", "plain": "User said yes to ship in plain words", "required": True},
    ]
    ok = security_ok  # review + user yes are human; agent must still ask
    user_line = (
        "Ship gate: "
        + ("security PASS. " if security_ok else "security FAIL — fix first. ")
        + "Open review pane, then say YES to ship. Nothing ships without your yes."
    )
    if findings:
        user_line += " " + " ".join(findings[:2])
    return {
        "ok": ok,
        "security_ok": security_ok,
        "checks": checks,
        "findings": findings,
        "user_line": user_line,
        "force": False,
    }


# --- 25: Sites ---

def sites_howto() -> dict[str, Any]:
    return {
        "id": "sites",
        "native": "Codex Sites (public beta)",
        "cost": "hungry",
        "user_line": _tag(
            "hungry",
            "Want it on the web without your own server? Codex Sites can host it. "
            "Save a version first, then deploy when you are ready. Live URL is production. You decide.",
        ),
        "agent_line": (
            "Wrap Sites. Do not invent hosting. Ask to save version before deploy. "
            "Run security gate first. User decides."
        ),
        "maturity": "beta",
    }


# --- menu ---

def all_features() -> list[dict[str, Any]]:
    return [
        goal_howto(),
        notifications_howto(),
        cloud_howto(),
        {
            "id": "walkthrough",
            "native": "ACC plain narration",
            "cost": "cheap",
            "user_line": _tag("cheap", "ACC says what it is doing in short plain lines while you walk away."),
            "agent_line": "Use walkthrough_line for every build step.",
        },
        review_gate_howto(),
        sites_howto(),
    ]


def plain_menu() -> str:
    lines = ["Walk-away tools (native Codex + ACC plain wrap). You choose:"]
    for f in all_features():
        lines.append(f"- {f['id']}: {f['user_line']}")
    lines.append("Nothing forced. Long work → prefer /goal. Ship → review + security + your yes.")
    return "\n".join(lines)


def suggest_for_request(request: str) -> list[str]:
    """Cheap suggestions for a user request."""
    low = (request or "").lower()
    out: list[str] = []
    if should_suggest_cloud(low) or any(w in low for w in ("long", "overnight", "walk away")):
        out.append(goal_howto()["user_line"])
        out.append(cloud_howto()["user_line"])
        out.append(notifications_howto()["user_line"])
    if any(w in low for w in ("ship", "deploy", "release", "go live", "publish")):
        out.append(review_gate_howto()["user_line"])
        out.append(sites_howto()["user_line"] if "site" in low or "host" in low or "web" in low else review_gate_howto()["user_line"])
    if any(w in low for w in ("host", "sites", "put it online", "public url")):
        out.append(sites_howto()["user_line"])
    if not out:
        out.append(_tag("cheap", "For multi-step work use /goal. For pings turn on notifications. You choose."))
    # unique preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for line in out:
        if line not in seen:
            seen.add(line)
            uniq.append(line)
    return uniq
