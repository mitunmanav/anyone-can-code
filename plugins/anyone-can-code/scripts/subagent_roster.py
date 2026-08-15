#!/usr/bin/env python3
"""Suggest Codex subagent role prompts (explorer / worker / reviewer).

Prompts only — never writes .codex/agents/*.toml or any project file.
Built-ins map to Codex explorer/worker; reviewer is a common custom-agent
pattern (see Codex Subagents docs + Copilot agent-profile analog).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# Codex built-ins: default, worker, explorer.
# reviewer = paste-ready role (optional user-owned custom agent TOML).
ROLE_CATALOG: list[dict[str, str]] = [
    {
        "role": "explorer",
        "agent_type": "explorer",
        "scope": "read-only",
        "when": "Map code, find files, gather evidence. No edits.",
        "expected": "bullets with file:line refs; no patches",
        "note": "Codex built-in explorer (read-heavy).",
    },
    {
        "role": "worker",
        "agent_type": "worker",
        "scope": "read-write",
        "when": "Implement one bounded job or fix. One write owner.",
        "expected": "short card: files touched / pass-fail / what changed",
        "note": "Codex built-in worker (execution-focused).",
    },
    {
        "role": "reviewer",
        "agent_type": "reviewer",
        "scope": "read-only",
        "when": "Review for correctness, security, regressions, missing tests.",
        "expected": "findings by severity with file:line; no style-only noise",
        "note": "Not a Codex built-in — prompt role (or user pastes custom TOML).",
    },
]

CORE_ORDER = ("explorer", "worker", "reviewer")


def _spawn_prompt(
    *,
    role: str,
    agent_type: str,
    scope: str,
    job: str,
    scope_hint: str,
    expected: str,
) -> str:
    job_line = job or f"({role}) do the assigned slice only"
    scope_line = scope_hint or f"project; {scope} unless parent says else"
    return (
        "Spawn a subagent.\n"
        f"Agent: {agent_type}\n"
        f"Job: {job_line}\n"
        f"Scope: {scope_line} ({scope})\n"
        f"Expected output: {expected}\n"
        "Speak caveman style: simple, short, direct, clear YES/NO, no ceremony."
    )


def _toml_snippet(role: dict[str, str]) -> str:
    """Pasteable custom-agent TOML (user may save under .codex/agents/). Never written by ACC."""
    name = role["role"]
    if name == "explorer":
        desc = "Read-heavy codebase exploration agent."
        instructions = (
            "Stay in exploration mode.\n"
            "Trace real paths, cite files and symbols.\n"
            "No code changes unless the parent agent asks."
        )
        sandbox = "read-only"
    elif name == "worker":
        desc = "Execution-focused agent for implementation and fixes."
        instructions = (
            "Own one bounded job.\n"
            "Smallest defensible change; leave unrelated files alone.\n"
            "Validate only what you changed; return a short pass-fail card."
        )
        sandbox = "workspace-write"
    else:
        desc = "PR reviewer focused on correctness, security, and missing tests."
        instructions = (
            "Review code like an owner.\n"
            "Prioritize correctness, security, regressions, missing tests.\n"
            "Lead with concrete findings; avoid style-only comments."
        )
        sandbox = "read-only"
    return (
        f'name = "{name}"\n'
        f'description = "{desc}"\n'
        f'sandbox_mode = "{sandbox}"\n'
        "developer_instructions = \"\"\"\n"
        f"{instructions}\n"
        '"""\n'
    )


def suggest_roster(
    *,
    goal: str | None = None,
    scope_hint: str | None = None,
    roles: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return role cards with ready-to-paste spawn prompts. Never writes."""
    want: list[str]
    if roles:
        allowed = {r["role"] for r in ROLE_CATALOG}
        want = [r for r in roles if r in allowed]
    else:
        want = list(CORE_ORDER)

    by_name = {r["role"]: r for r in ROLE_CATALOG}
    job = (goal or "").strip()
    scope = (scope_hint or "").strip()
    out: list[dict[str, Any]] = []
    for name in want:
        base = by_name[name]
        card = {
            "role": base["role"],
            "agent_type": base["agent_type"],
            "scope": base["scope"],
            "when": base["when"],
            "note": base["note"],
            "spawn_prompt": _spawn_prompt(
                role=base["role"],
                agent_type=base["agent_type"],
                scope=base["scope"],
                job=job,
                scope_hint=scope,
                expected=base["expected"],
            ),
            "toml_snippet": _toml_snippet(base),
        }
        out.append(card)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Suggest Codex subagent role prompts (explorer/worker/reviewer). "
            "Prompts only — never writes agent TOML."
        )
    )
    parser.add_argument(
        "--goal",
        default="",
        help="Job text filled into each spawn prompt",
    )
    parser.add_argument(
        "--scope",
        default="",
        dest="scope_hint",
        help="Scope path/dir hint filled into each spawn prompt",
    )
    parser.add_argument(
        "--roles",
        default="",
        help="Comma list: explorer,worker,reviewer (default: all three)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Ignored (suggest-only; kept for CLI symmetry with other helpers)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON object with roles list",
    )
    args = parser.parse_args(argv)
    role_list = [r.strip() for r in args.roles.split(",") if r.strip()] or None
    roles = suggest_roster(
        goal=args.goal or None,
        scope_hint=args.scope_hint or None,
        roles=role_list,
    )
    if args.json:
        print(json.dumps({"roles": roles, "count": len(roles)}, indent=2))
        return 0
    if not roles:
        print("No roles matched. Use explorer, worker, and/or reviewer.")
        return 0
    print(f"{len(roles)} role(s) — prompts only; ACC never writes agent TOML:")
    for i, role in enumerate(roles, 1):
        print(f"\n## {i}. {role['role']} ({role['scope']}) — {role['when']}")
        print(role["spawn_prompt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
