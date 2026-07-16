"""Subagent hooks: inject rules at start, log the result at stop."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state

START_CONTEXT = (
    "You are a subagent for Anyone Can Code. Do ONLY the job and scope you were given "
    "— no extra files, no side quests. Speak caveman style: simple, short, bullets, "
    "clear YES/NO, no ceremony. Report what you verified, not what you assume. "
    "[HUNGRY] You spend extra tokens — stay narrow. Prefer light reasoning. "
    "No git push, no deploy, no secrets. Return a short summary only."
)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    event = payload.get("hook_event_name", "")
    if event == "SubagentStart":
        state.append_jsonl(
            state.signal_log_path(repo_root),
            {"timestamp": state.utc_now(), "signal_type": "subagent_start",
             "detail": payload.get("agent_type", "unknown"),
             "turn_id": payload.get("turn_id")},
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": START_CONTEXT,
            }
        }
    if event == "SubagentStop":
        message = (payload.get("last_assistant_message") or "")[:200]
        state.append_jsonl(
            state.signal_log_path(repo_root),
            {"timestamp": state.utc_now(), "signal_type": "subagent_result",
             "detail": f"{payload.get('agent_type', 'unknown')}: {message}",
             "turn_id": payload.get("turn_id")},
        )
    return {}


def main() -> None:
    payload = json.load(sys.stdin)
    resolution = state.resolve_hook_project(payload)
    print(
        json.dumps(
            state.run_hook_attempt(
                resolution,
                "subagent",
                payload,
                lambda: handle_payload(payload, Path(resolution["project_root"])),
            )
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # pragma: no cover - hook best effort
        print(json.dumps({}))
