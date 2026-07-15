#!/usr/bin/env python3
"""Loop registry — work / scheduled / self-improve (wrap native, never rebuild).

Item 7: plain map of ACC loops onto Codex powers.
- work: in-session loop_budget (front_door already)
- scheduled: native Codex Scheduled tasks + automations/ prompts
- self-improve: free session_self_learn (0 tokens); AI deep audit is separate opt-in

Nothing forced. User turns scheduled loops on in Codex UI.
"""

from __future__ import annotations

from typing import Any


LOOPS: dict[str, dict[str, Any]] = {
    "work": {
        "name": "Work loop",
        "plain": "Keep building the current task until budget ends, then prove real use or ask you.",
        "native": "ACC loop_budget + execute skill (in this chat)",
        "token": "hungry",  # uses the live chat model
        "opt_in": False,  # always available when building
        "setup": "Just ask ACC to build. It stops after loop_budget and asks for real-use proof.",
    },
    "scheduled": {
        "name": "Scheduled loop",
        "plain": "Codex runs a short check on a clock while your PC is on.",
        "native": "Codex Desktop Scheduled tasks (automations/)",
        "token": "hungry",  # each run spends tokens
        "opt_in": True,
        "setup": (
            "Only if you want it: Codex sidebar → Scheduled → New → "
            "paste a prompt from automations/ → pick time → pick project. "
            "You can say no. Machine must stay on."
        ),
    },
    "self_improve": {
        "name": "Self-improve loop",
        "plain": "Learn from past chats on disk for free, then optionally save lessons.",
        "native": "scripts/session_self_learn.py over ~/.codex/sessions",
        "token": "cheap",  # zero AI tokens
        "opt_in": True,
        "setup": (
            "Run: python scripts/session_self_learn.py --project-root . "
            "Add --write only when you want lessons saved. No auto write."
        ),
    },
}


def list_loops() -> list[dict[str, Any]]:
    return [dict(v, id=k) for k, v in LOOPS.items()]


def describe_loop(loop_id: str) -> dict[str, Any] | None:
    key = (loop_id or "").strip().lower().replace("-", "_")
    if key not in LOOPS:
        return None
    return dict(LOOPS[key], id=key)


def plain_menu() -> str:
    """Short user-facing menu. Nothing forced."""
    lines = [
        "ACC loops (you choose):",
        "1) Work — build now in this chat (stops at budget, asks for proof).",
        "2) Scheduled — optional clock jobs in Codex (PC must stay on).",
        "3) Self-improve — free learn from past sessions (0 AI tokens).",
        "Say which you want. Scheduled and self-improve stay OFF until you turn them on.",
    ]
    return "\n".join(lines)


def scheduled_opt_in_question() -> str:
    return (
        "Set up scheduled checks? [HUNGRY each run] "
        "Only if you want. PC must stay on. YES = I help you paste a prompt in Codex Scheduled. NO = skip."
    )
