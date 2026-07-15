#!/usr/bin/env python3
"""Browser test policy — prefer connected Chrome; never force built-in browser.

Audit: Codex built-in browser testing crashed the app (Codex bug, we cannot fix).
Docs: built-in browser vs Chrome extension are both real Codex tools.
ACC rule: explain plain, route to Chrome for test/verify, user decides.
"""

from __future__ import annotations

from typing import Any


# Plain words for non-tech users
USER_EXPLAIN = (
    "Codex has its own mini browser for previews, but it can crash the app "
    "(a Codex bug, not your fault). Safer path: use your real Chrome with the "
    "Codex Chrome connection. You choose."
)

AGENT_RULE = (
    "Browser testing: do NOT use the built-in @Browser for long test loops. "
    "Prefer connected Chrome (@Chrome). Explain crash risk in plain words. "
    "Ask the user. User decides. Never force."
)


def browser_test_advice(*, needs_login: bool = False, user_prefers_builtin: bool = False) -> dict[str, Any]:
    """Return wrap-native advice. User always chooses."""
    if user_prefers_builtin:
        return {
            "recommended": "builtin",
            "tool": "@Browser",
            "force": False,
            "user_line": (
                "You asked for the mini browser. OK. "
                "If the app freezes or crashes, switch to Chrome and say so."
            ),
            "agent_line": AGENT_RULE,
        }
    reason = "Safer for test loops; uses your real Chrome."
    if needs_login:
        reason = "Needs your signed-in tabs; Chrome is the right tool."
    return {
        "recommended": "chrome",
        "tool": "@Chrome",
        "force": False,
        "user_line": USER_EXPLAIN + " " + reason + " Want Chrome, or try mini browser anyway?",
        "agent_line": AGENT_RULE,
    }
