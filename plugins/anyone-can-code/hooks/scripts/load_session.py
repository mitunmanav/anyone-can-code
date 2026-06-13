"""
Load small session context.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


def find_repo_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return None


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


def main() -> None:
    payload = json.load(sys.stdin)
    repo_root = find_repo_root()
    if repo_root is None:
        print(json.dumps({}))
        return

    source = payload.get("source", "startup")
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": build_context(repo_root, source),
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - hook best effort
        print(json.dumps({"systemMessage": f"load_session.py: {exc}"}))
