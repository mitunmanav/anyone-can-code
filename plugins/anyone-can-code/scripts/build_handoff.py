#!/usr/bin/env python3
"""Build a full-context handoff prompt for a new Codex thread."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import canonical_state  # noqa: E402
import memory_preflight  # noqa: E402

try:
    import cross_agent_pack
except Exception:  # pragma: no cover
    cross_agent_pack = None  # type: ignore

STYLE_BLOCK = """Communication:
- strict caveman style: short, direct, simple. Technical terms exact.
- user is non-technical. Explain outcomes plainly.
- ACC orchestrator stays workflow owner. Other skills advisory only."""


def git_status(root: Path) -> str:
    import subprocess
    try:
        out = subprocess.run(["git", "status", "--short"], cwd=root,
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or "clean"
    except (OSError, subprocess.SubprocessError):
        return "git unavailable"


def build_prompt(
    root: Path,
    *,
    model: str | None = None,
    reasoning: str | None = None,
) -> str:
    state = canonical_state.read_canonical_state(root)
    goal = state.get("active_goal") or "project status"
    try:
        memory = memory_preflight.retrieve_relevant_memory(root, goal)
        memory_lines = [f"- {item.get('summary')}" for item in memory["items"]]
    except Exception as error:  # memory must never block a handoff
        memory_lines = [f"- (memory unavailable: {error})"]

    model_block = ""
    if model:
        reason = (reasoning or "medium").strip()
        model_block = f"\nTarget model: {model.strip()} (reasoning={reason})\n"

    env_block = ""
    if cross_agent_pack is not None:
        env_block = f"\n{cross_agent_pack.env_agent_line()}\n"

    return f"""Continue work in this same local project. Do not fork.

{STYLE_BLOCK}
{model_block}{env_block}
Project root: {root}
Active goal: {goal}
Active task: {state.get('active_task') or '(none)'}
Next action: {state.get('next_action') or '(none)'}

Relevant memory:
{chr(10).join(memory_lines) or '- none'}

Git status (short):
{git_status(root)}

Rules: verify before done. No push/PR/release without explicit user command.
No done without proof. ACC orchestrator stays workflow owner."""


def main() -> None:
    parser = argparse.ArgumentParser(description="ACC handoff prompt builder")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--model", default="", help="Target model for switch handoff")
    parser.add_argument("--reasoning", default="", help="Target reasoning effort")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    print(
        build_prompt(
            root,
            model=args.model or None,
            reasoning=args.reasoning or None,
        )
    )


if __name__ == "__main__":
    main()
