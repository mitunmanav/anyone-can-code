#!/usr/bin/env python3
"""Build handoff: write portable file + print Codex-friendly prompt.

Native Codex (docs): codex resume / codex exec resume / app-server
thread/start|resume|fork. ACC adds PORTABLE_HANDOFF.md for any tool/model.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import canonical_state  # noqa: E402
import memory_preflight  # noqa: E402
import portable_handoff  # noqa: E402

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


def write_handoff_file(
    root: Path,
    *,
    model: str | None = None,
    reasoning: str | None = None,
    tool_left: str = "codex",
    session_id: str = "",
) -> dict:
    state = canonical_state.read_canonical_state(root)
    return portable_handoff.write_portable_handoff(
        root,
        state,
        tool_left=tool_left,
        session_id=session_id or "",
        summary=str(state.get("active_task") or ""),
    )


def build_prompt(
    root: Path,
    *,
    model: str | None = None,
    reasoning: str | None = None,
    tool_left: str = "codex",
    session_id: str = "",
    write_file: bool = True,
) -> str:
    state = canonical_state.read_canonical_state(root)
    goal = state.get("active_goal") or "project status"
    try:
        memory = memory_preflight.retrieve_relevant_memory(root, goal)
        memory_lines = [f"- {item.get('summary')}" for item in memory["items"]]
    except Exception as error:  # memory must never block a handoff
        memory_lines = [f"- (memory unavailable: {error})"]

    write_info = {"path": str(portable_handoff.portable_path(root)), "written": False}
    if write_file:
        write_info = write_handoff_file(
            root,
            model=model,
            reasoning=reasoning,
            tool_left=tool_left,
            session_id=session_id,
        )

    model_block = ""
    if model:
        reason = (reasoning or "medium").strip()
        model_block = f"\nTarget model: {model.strip()} (reasoning={reason})\n"

    env_block = ""
    if cross_agent_pack is not None:
        env_block = f"\n{cross_agent_pack.env_agent_line()}\n"

    handoff_path = portable_handoff.REL_PATH.as_posix()
    sid = (session_id or "").strip()
    native_line = (
        f"If still on Codex and session known ({sid}): prefer native "
        "`codex resume` / `codex exec resume` / app-server `thread/resume` "
        "before re-deriving. New Codex thread: app-server `thread/start` "
        "(or Desktop new task) with this prompt — not fork unless user asks "
        "(`thread/fork`)."
        if sid
        else (
            "If still on Codex same chat: prefer native `codex resume --last` "
            "or app-server `thread/resume`. New Codex thread: `thread/start` "
            "or Desktop new task with this prompt. Do not fork unless user asks."
        )
    )

    return f"""Continue work in this same local project.

{STYLE_BLOCK}
{model_block}{env_block}
Portable handoff file (any tool/model — open first):
  {handoff_path}
  written={write_info.get('written')} path={write_info.get('path')}

Project root: {root}
Active goal: {goal}
Active task: {state.get('active_task') or '(none)'}
Next action: {state.get('next_action') or '(none)'}

Relevant memory:
{chr(10).join(memory_lines) or '- none'}

Git status (short):
{git_status(root)}

Native Codex: {native_line}
Rules: verify before done. No push/PR/release without explicit user command.
No done without proof. ACC orchestrator stays workflow owner.
Update {handoff_path} before stopping again."""


def main() -> None:
    parser = argparse.ArgumentParser(description="ACC handoff prompt builder")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--model", default="", help="Target model for switch handoff")
    parser.add_argument("--reasoning", default="", help="Target reasoning effort")
    parser.add_argument("--tool-left", default="codex")
    parser.add_argument("--session-id", default="")
    parser.add_argument(
        "--write-only",
        action="store_true",
        help="Only write PORTABLE_HANDOFF.md (no stdout prompt)",
    )
    parser.add_argument(
        "--stdout-only",
        action="store_true",
        help="Print prompt without writing the portable file",
    )
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if args.write_only:
        info = write_handoff_file(
            root,
            model=args.model or None,
            reasoning=args.reasoning or None,
            tool_left=args.tool_left,
            session_id=args.session_id,
        )
        print(info.get("path", ""))
        return
    print(
        build_prompt(
            root,
            model=args.model or None,
            reasoning=args.reasoning or None,
            tool_left=args.tool_left,
            session_id=args.session_id,
            write_file=not args.stdout_only,
        )
    )


if __name__ == "__main__":
    main()
