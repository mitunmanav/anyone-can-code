#!/usr/bin/env python3
"""
Cheap host detect for wording only: cli | desktop | unknown.

No invent. Prefer env that is already set by host shells.
Never claims Desktop-only features work on CLI.
"""

from __future__ import annotations

import os
import sys


def detect_host(env: dict | None = None) -> str:
    """Return 'cli' | 'desktop' | 'unknown'."""
    e = env if env is not None else os.environ

    # Explicit override for tests / advanced users (local only; not a Codex API).
    forced = str(e.get("ACC_HOST") or "").strip().lower()
    if forced in {"cli", "desktop", "unknown"}:
        return forced

    # Common terminal / TUI signals (cheap heuristics; not official Codex fields).
    term_program = str(e.get("TERM_PROGRAM") or "").lower()
    if term_program in {"vscode", "cursor"}:
        # Still may be CLI inside IDE terminal → unknown unless more signal.
        pass

    # Codex app often sets product-ish markers when present in some builds;
    # if absent, stay unknown rather than guess wrong.
    for key in ("CODEX_APP", "CODEX_DESKTOP", "CHATGPT_DESKTOP"):
        val = str(e.get(key) or "").strip().lower()
        if val in {"1", "true", "yes", "desktop", "app"}:
            return "desktop"

    for key in ("CODEX_CLI", "CODEX_TUI"):
        val = str(e.get(key) or "").strip().lower()
        if val in {"1", "true", "yes", "cli", "tui"}:
            return "cli"

    # Interactive tty without desktop markers → likely CLI session.
    if sys.stdin.isatty() and sys.stdout.isatty():
        # Only when ACC_HOST not forced; still weak → prefer unknown for wording safety?
        # Plan: safe unknown when docs/env insufficient. TTY alone is weak.
        return "unknown"

    return "unknown"


def host_guidance(host: str | None = None) -> dict:
    """Plain strings for skills (no AI)."""
    h = host or detect_host()
    if h == "cli":
        return {
            "host": "cli",
            "install": "In Codex CLI: /plugins → install Anyone Can Code. Then /hooks → trust ACC hooks. Then $setup.",
            "review": "Before ship: /review",
            "long_job": "Long job: /goal",
            "model": "Model: /model",
            "sites": "Sites host UI is Desktop-first. Use Codex app if you need Sites.",
            "scheduled": "Scheduled tasks UI is Desktop-first. Use Codex app if you need the clock UI.",
        }
    if h == "desktop":
        return {
            "host": "desktop",
            "install": "In Codex app: Plugins → install Anyone Can Code. Trust hooks when asked. Then $setup.",
            "review": "Before ship: use Review in the app (or /review if available).",
            "long_job": "Long job: /goal",
            "model": "Pick model in the app model menu (or /model if available).",
            "sites": "Sites: use Codex Sites when you want hosting. User decides.",
            "scheduled": "Scheduled: Codex Settings automations. Ask before enabling.",
        }
    return {
        "host": "unknown",
        "install": "Install Anyone Can Code from Plugins (/plugins in CLI, or Plugins in the app). Trust hooks (/hooks in CLI). Then $setup.",
        "review": "Before ship: /review (CLI) or Review pane (app).",
        "long_job": "Long job: /goal",
        "model": "Model: /model (CLI) or model menu (app).",
        "sites": "Sites host UI is Desktop-first.",
        "scheduled": "Scheduled clock UI is Desktop-first.",
    }


def main(argv: list[str] | None = None) -> int:
    import json

    argv = list(sys.argv[1:] if argv is None else argv)
    host = detect_host()
    if "--guidance" in argv:
        print(json.dumps(host_guidance(host), indent=2))
    else:
        print(json.dumps({"host": host}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
