"""
Load small session context.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


def read_agents_md(repo_root: Path) -> str:
    path = repo_root / "AGENTS.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")[:2000]
        except OSError:
            return ""
    return ""


def build_context(repo_root: Path, source: str) -> str:
    workflow = state.read_state(repo_root)
    prefs = state.read_preferences(repo_root)
    agents = read_agents_md(repo_root)
    context_lines = [
        f"State: {workflow.get('phase', 'idle')} / {workflow.get('route', 'unknown')}.",
        f"Next: {workflow.get('next_step', 'N/A')}.",
        f"Talk: {prefs.get('communication_mode', 'caveman-strict')}.",
        f"Memory: {workflow.get('memory_mode', 'portable-markdown')}.",
        f"From: {source}.",
    ]
    if agents:
        context_lines.append("")
        context_lines.append("Project rules:")
        context_lines.append(agents)
    return "\n".join(context_lines)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    source = payload.get("source", "startup")
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(repo_root, source),
        }
    }


def main() -> None:
    payload = json.load(sys.stdin)
    resolution = state.resolve_hook_project(payload)
    print(
        json.dumps(
            state.run_hook_attempt(
                resolution,
                "load_session",
                payload,
                lambda: handle_payload(payload, Path(resolution["project_root"])),
            )
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - hook best effort
        print(json.dumps({}))
