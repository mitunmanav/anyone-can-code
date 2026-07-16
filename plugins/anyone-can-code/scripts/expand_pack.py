#!/usr/bin/env python3
"""Phase F — expand: CLI host + other agents later.

Wrap native Codex plugin model. No fake Claude/Cursor ports.
Explain → suggest → user decides. [CHEAP]/[HUNGRY].
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
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


# --- 33: Codex CLI port (same plugin bundle) ---

def detect_host(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Which Codex surface is running. Same plugin; different shell."""
    context = context or {}
    surface = _norm(context.get("surface") or context.get("host") or context.get("app"))
    if surface in {"cli", "terminal", "tui"}:
        hid = "cli"
    elif surface in {"exec", "headless", "noninteractive", "ci"}:
        hid = "exec"
    elif surface in {"desktop", "app", "windows app", "chatgpt desktop"}:
        hid = "desktop"
    elif surface in {"ide", "vscode", "extension"}:
        hid = "ide"
    else:
        import os

        if os.environ.get("CI") or os.environ.get("CODEX_CI"):
            hid = "exec"
        else:
            hid = "desktop"

    lines = {
        "desktop": "Host: Codex Desktop. Full UI (review pane, Sites, notifications).",
        "cli": "Host: Codex CLI. Same plugin skills/hooks. Use terminal commands and /slash.",
        "exec": "Host: codex exec (headless). Scripts/CI. Default sandbox read-only.",
        "ide": "Host: Codex IDE extension. Same plugin model; editor-first.",
    }
    return {
        "id": hid,
        "supports_plugins": True,
        "user_line": lines.get(hid, lines["desktop"]),
        "agent_line": (
            "One ACC plugin bundle for Desktop + CLI + IDE. "
            "Do not rebuild per host. Adapt UI words to the host."
        ),
    }


def cli_howto() -> dict[str, Any]:
    return {
        "id": "cli_port",
        "native": "Codex CLI plugin directory (same plugin.json bundle)",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Want ACC in the terminal? Install the same Anyone Can Code plugin in Codex CLI. "
            "Same plan → build → verify. No second product. You choose Desktop or CLI.",
        ),
        "agent_line": (
            "CLI port = same plugin. Guide install from marketplace or local path. "
            "Hooks/skills/MCP work when CLI supports plugins. Prefer python3 scripts."
        ),
        "setup_steps": [
            "Install Codex CLI and sign in",
            "Add ACC marketplace or install local plugin folder (same .codex-plugin/plugin.json)",
            "Open a project folder in the terminal",
            "Run codex, then use ACC skills ($setup, plan, build, verify)",
            "Doctor: python plugins/anyone-can-code/scripts/doctor.py",
        ],
    }


# --- 34: other agents — honest later ---

def other_agents_howto() -> dict[str, Any]:
    return {
        "id": "other_agents",
        "native": "None yet (Codex-first)",
        "cost": "cheap",
        "status": "later",
        "force": False,
        "user_line": _tag(
            "cheap",
            "Claude, Cursor, and other agents: not yet. Codex first (Desktop + CLI). "
            "If you switch tools, say handoff so context can travel. Nothing forced.",
        ),
        "agent_line": (
            "Do not claim ACC runs on Claude/Cursor today. "
            "Other-agent ports are later. Offer handoff/export of state if user leaves Codex."
        ),
    }


def all_features() -> list[dict[str, Any]]:
    return [cli_howto(), other_agents_howto()]


def plain_menu() -> str:
    lines = ["Expand tools (Codex first). You choose:"]
    for f in all_features():
        lines.append(f"- {f['id']}: {f['user_line']}")
    lines.append("Other agents = later. Nothing forced.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="ACC Phase F expand helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_host = sub.add_parser("host", help="Detect Codex host surface")
    p_host.add_argument("--surface", default="")
    p_host.add_argument("--json", action="store_true")

    p_menu = sub.add_parser("menu", help="Plain expand menu")
    p_menu.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.cmd == "host":
        h = detect_host({"surface": args.surface} if args.surface else None)
        if args.json:
            print(json.dumps(h, indent=2))
        else:
            print(h["user_line"])
        return
    if args.cmd == "menu":
        if args.json:
            print(json.dumps(all_features(), indent=2))
        else:
            print(plain_menu())


if __name__ == "__main__":
    main()
