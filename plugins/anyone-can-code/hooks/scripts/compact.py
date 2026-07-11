"""PreCompact hook: freeze the working capsule before Codex compresses context."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


def handle_payload(payload: dict, repo_root: Path) -> dict:
    workflow = state.read_state(repo_root)
    steps = workflow.get("next_steps") or []
    lines = [
        "# Compact Capsule",
        f"Saved: {state.utc_now()} (trigger: {payload.get('trigger', 'unknown')})",
        f"Goal: {workflow.get('active_goal') or workflow.get('active_task') or 'not set'}",
        f"Next: {workflow.get('next_action') or workflow.get('next_step') or 'not set'}",
    ]
    for step in steps:
        marker = "x" if step.get("status") == "done" else " "
        lines.append(f"- [{marker}] {step.get('step', '')}")
    layout = state.ensure_project_layout(repo_root)
    (layout["state"] / "compact-capsule.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    state.append_jsonl(
        state.signal_log_path(repo_root),
        {"timestamp": state.utc_now(), "signal_type": "compaction",
         "detail": f"capsule saved ({payload.get('trigger', 'unknown')})",
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
                "compact",
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
