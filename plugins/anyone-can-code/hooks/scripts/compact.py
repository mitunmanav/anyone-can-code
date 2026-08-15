"""PreCompact + PostCompact: announce shrink, save capsule, re-inject goal/next.

Docs (hooks): PreCompact/PostCompact support common output fields including
systemMessage. PostCompact does NOT document additionalContext — use
systemMessage for re-inject. SessionStart source=compact also re-anchors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state


def _capsule_path(repo_root: Path) -> Path:
    layout = state.ensure_project_layout(repo_root)
    return layout["state"] / "compact-capsule.md"


def _read_goal_next(repo_root: Path) -> tuple[str, str, list[dict]]:
    workflow = state.read_state(repo_root)
    goal = str(workflow.get("active_goal") or workflow.get("active_task") or "not set")
    nxt = str(workflow.get("next_action") or workflow.get("next_step") or "not set")
    steps = workflow.get("next_steps") or []
    if not isinstance(steps, list):
        steps = []
    return goal, nxt, steps


def write_capsule(repo_root: Path, trigger: str) -> Path:
    goal, nxt, steps = _read_goal_next(repo_root)
    lines = [
        "# Compact Capsule",
        f"Saved: {state.utc_now()} (trigger: {trigger})",
        f"Goal: {goal}",
        f"Next: {nxt}",
    ]
    for step in steps:
        if not isinstance(step, dict):
            continue
        marker = "x" if step.get("status") == "done" else " "
        lines.append(f"- [{marker}] {step.get('step', '')}")
    path = _capsule_path(repo_root)
    import memory_core

    memory_core.atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def handle_pre_compact(payload: dict, repo_root: Path) -> dict:
    trigger = str(payload.get("trigger") or "unknown")
    write_capsule(repo_root, trigger)
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import context_rot as _context_rot  # type: ignore

        if _context_rot.exists(repo_root):
            _context_rot.append_capsule_pointer(
                repo_root,
                pointer="state/compact-capsule.md",
                note=f"pre-compact:{trigger}",
            )
    except Exception:
        pass
    state.append_jsonl(
        state.signal_log_path(repo_root),
        {
            "timestamp": state.utc_now(),
            "signal_type": "compaction",
            "detail": f"pre-compact capsule saved ({trigger})",
            "turn_id": payload.get("turn_id"),
        },
    )
    # systemMessage = user-visible warn (docs common output fields)
    return {
        "systemMessage": (
            "ACC: Chat is about to shrink (compact). "
            "Saving your goal and next steps first. This is not a crash."
        )
    }


def handle_post_compact(payload: dict, repo_root: Path) -> dict:
    trigger = str(payload.get("trigger") or "unknown")
    goal, nxt, _ = _read_goal_next(repo_root)
    capsule = _capsule_path(repo_root)
    if capsule.exists():
        try:
            text = capsule.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("Goal:"):
                    goal = line.split(":", 1)[1].strip() or goal
                elif line.startswith("Next:"):
                    nxt = line.split(":", 1)[1].strip() or nxt
        except OSError:
            pass
    state.append_jsonl(
        state.signal_log_path(repo_root),
        {
            "timestamp": state.utc_now(),
            "signal_type": "compaction",
            "detail": f"post-compact re-inject ({trigger})",
            "turn_id": payload.get("turn_id"),
        },
    )
    # Re-inject via systemMessage (documented for PostCompact). Keep short.
    goal_s = goal[:160]
    next_s = nxt[:160]
    return {
        "systemMessage": (
            f"ACC: Context was shortened. Goal: {goal_s}. Next: {next_s}. "
            "Do not re-ask answered questions. Re-read capsule if unsure."
        )
    }


def handle_payload(payload: dict, repo_root: Path) -> dict:
    event = str(
        payload.get("hook_event_name")
        or payload.get("hookEventName")
        or ""
    ).lower()
    if "postcompact" in event or event == "post_compact":
        return handle_post_compact(payload, repo_root)
    # Default PreCompact (also when event blank for older callers)
    return handle_pre_compact(payload, repo_root)


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
