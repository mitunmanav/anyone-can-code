#!/usr/bin/env python3
"""Portable cross-tool handoff — model-neutral work bag for ACC.

Wraps Codex native resume (docs: codex resume / codex exec resume /
app-server thread/resume|start|fork). Does NOT re-implement rollouts.

Writes project-local:
  .codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md

Docs stamp (local codex-docs-chunked.jsonl):
  - noninteractive: resume --last / session id; --ephemeral skips rollouts
  - cli/features: codex resume for saved sessions
  - hooks: SessionStart source startup|resume|clear|compact; session_id on stdin;
    Stop last_assistant_message; PreCompact plain stdout ignored
  - app-server: thread/start, thread/resume, thread/fork (not invent create_thread)
  - remote-connections: host task handoff only (not cross-model)
  - memories: native ~/.codex/memories separate; ACC uses portable markdown only
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

SCHEMA = "acc-portable-handoff/1"
REL_PATH = Path(".codex") / "anyone-can-code" / "artifacts" / "PORTABLE_HANDOFF.md"
MAX_BYTES = 12_000
MAX_PLAN_STEPS = 20
MAX_MEMORY_FACTS = 12
MAX_FIELD = 400

# Secret scrub — keep private-file rules; never put keys in handoff.
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|authorization)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"(?i)\b(sk-[a-z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|xox[baprs]-[a-zA-Z0-9-]{20,})\b"),
    re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*"),
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def portable_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / REL_PATH


def redact(text: str) -> str:
    out = str(text or "")
    for pattern in _SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def _clip(text: Any, limit: int = MAX_FIELD) -> str:
    raw = redact(str(text or "").strip())
    if len(raw) <= limit:
        return raw
    return raw[: limit - 3].rstrip() + "..."


def _plan_lines(state: dict[str, Any]) -> list[str]:
    plan = state.get("plan") or state.get("next_steps") or []
    lines: list[str] = []
    if isinstance(plan, list):
        for item in plan[:MAX_PLAN_STEPS]:
            if isinstance(item, dict):
                text = item.get("text") or item.get("step") or item.get("title") or ""
                done = bool(item.get("done") or item.get("completed"))
            else:
                text = str(item)
                done = text.startswith("[x]") or text.startswith("[X]")
            text = _clip(re.sub(r"^\[[ xX]\]\s*", "", text), 200)
            if not text:
                continue
            mark = "x" if done else " "
            lines.append(f"- [{mark}] {text}")
    if not lines:
        next_action = _clip(state.get("next_action") or state.get("next_step") or "")
        if next_action:
            lines.append(f"- [ ] {next_action}")
        else:
            lines.append("- [ ] (no plan steps yet — set next action)")
    return lines


def _memory_facts(repo_root: Path, state: dict[str, Any]) -> list[str]:
    facts: list[str] = []
    try:
        import memory_preflight  # type: ignore

        goal = state.get("active_goal") or state.get("active_task") or "project"
        result = memory_preflight.retrieve_relevant_memory(Path(repo_root), str(goal))
        for item in (result.get("items") or [])[:MAX_MEMORY_FACTS]:
            summary = _clip(item.get("summary") or "", 160)
            if summary:
                facts.append(f"- {summary}")
    except Exception:
        pass
    if not facts:
        try:
            import wiki_memory  # type: ignore

            memory_root = Path(repo_root) / ".codex" / "anyone-can-code" / "memory"
            brief = wiki_memory.session_brief(memory_root, max_chars=600)
            for line in (brief or "").splitlines():
                line = line.strip()
                if line.startswith("-"):
                    facts.append(_clip(line, 160))
                if len(facts) >= MAX_MEMORY_FACTS:
                    break
        except Exception:
            pass
    return facts[:MAX_MEMORY_FACTS]


def _verification_line(state: dict[str, Any]) -> str:
    ver = state.get("verification") if isinstance(state.get("verification"), dict) else {}
    level = ver.get("level") or "unverified"
    evidence = ver.get("evidence") or []
    if isinstance(evidence, list) and evidence:
        bits = [_clip(e, 80) for e in evidence[:3]]
        return f"{level}; evidence: " + "; ".join(bits)
    return str(level)


def _should_skip_empty(state: dict[str, Any], summary: str) -> bool:
    """Avoid overwriting a good handoff with an empty idle stop."""
    next_action = str(state.get("next_action") or state.get("next_step") or "").strip()
    goal = str(state.get("active_goal") or "").strip()
    task = str(state.get("active_task") or "").strip()
    if next_action or goal or task or summary.strip():
        return False
    return True


def build_markdown(
    repo_root: Path,
    state: dict[str, Any],
    *,
    tool_left: str = "codex",
    session_id: str = "",
    rollout_hint: str = "",
    summary: str = "",
    open_question: str = "",
) -> str:
    root = Path(repo_root).resolve()
    goal = _clip(state.get("active_goal") or "project status", 500)
    task = _clip(state.get("active_task") or state.get("last_task") or "(none)", 400)
    next_action = _clip(
        state.get("next_action")
        or state.get("next_step")
        or (summary and "Continue from last stop; re-check goal.")
        or "(set next action)",
        400,
    )
    boundaries = state.get("boundaries") or []
    if isinstance(boundaries, list):
        bound_text = "; ".join(_clip(b, 80) for b in boundaries[:5]) or "none listed"
    else:
        bound_text = _clip(boundaries, 200) or "none listed"

    memory_facts = _memory_facts(root, state)
    memory_block = "\n".join(memory_facts) if memory_facts else "- none yet"
    plan_block = "\n".join(_plan_lines(state))
    sid = _clip(session_id or "", 80) or "none"
    roll = _clip(Path(rollout_hint).name if rollout_hint else "", 120) or "none"
    oq = _clip(open_question or "none", 200)
    last = _clip(summary, 300) if summary else ""

    lines = [
        "# ACC portable handoff",
        f"schema: {SCHEMA}",
        f"updated_at: {utc_now()}",
        f"project_root: {root}",
        f"transaction_id: {_clip(state.get('transaction_id') or '', 80) or 'none'}",
        "",
        "## Where",
        f"- tool_left: {_clip(tool_left, 40)}",
        f"- session_id: {sid}",
        f"- rollout_hint: {roll}",
        "",
        "## Goal",
        goal,
        "",
        "## Plan",
        plan_block,
        "",
        "## State",
        f"- active_task: {task}",
        f"- verification: {_clip(_verification_line(state), 240)}",
        f"- boundaries: {bound_text}",
    ]
    if last:
        lines.append(f"- last_summary: {last}")
    lines += [
        "",
        "## Memory (pointers + top facts)",
        "- wiki: .codex/anyone-can-code/memory/wiki/index.md",
        "- notes: .codex/anyone-can-code/memory/notes/",
        f"- open_question: {oq}",
        memory_block,
        "",
        "## Next step",
        next_action,
        "",
        "## Don’t",
        "- no push/PR/release without user yes",
        "- no inventing missing context",
        "- secrets: never paste tokens/keys",
        "- do not rebuild Codex rollouts; use native resume when still on Codex",
        "",
        "## How to resume (any tool)",
        "1. Open this file.",
        "2. Open `.codex/anyone-can-code/state/workflow.json` if present (same transaction_id).",
        "3. If still on Codex and session_id set: try native resume first:",
        "   - CLI: `codex resume <session_id>` or `codex resume --last`",
        "   - non-interactive: `codex exec resume <SESSION_ID>` or `codex exec resume --last`",
        "   - app-server: `thread/resume` (or `thread/start` for a new thread; `thread/fork` only if user asks to fork)",
        "4. Else continue from Goal + Plan + Next step; load wiki/notes as needed.",
        "5. Update this file before stopping again.",
        "",
    ]
    text = "\n".join(lines)
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        text = encoded[:MAX_BYTES].decode("utf-8", errors="ignore")
        cut = text.rfind("\n")
        if cut > MAX_BYTES // 2:
            text = text[:cut] + "\n"
    return text


def write_portable_handoff(
    repo_root: Path,
    state: dict[str, Any] | None = None,
    *,
    tool_left: str = "codex",
    session_id: str = "",
    rollout_hint: str = "",
    summary: str = "",
    open_question: str = "",
    skip_if_empty: bool = False,
) -> dict[str, Any]:
    """Write PORTABLE_HANDOFF.md + short resume-note mirror. Returns status dict."""
    root = Path(repo_root).resolve()
    if state is None:
        try:
            import canonical_state  # type: ignore

            state = canonical_state.read_canonical_state(root)
        except Exception:
            state = {}
    state = state or {}
    summary = redact(summary or "")

    path = portable_path(root)
    if skip_if_empty and _should_skip_empty(state, summary) and path.exists():
        return {"written": False, "skipped": True, "path": str(path), "reason": "empty-idle"}

    text = build_markdown(
        root,
        state,
        tool_left=tool_left,
        session_id=session_id,
        rollout_hint=rollout_hint,
        summary=summary,
        open_question=open_question,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

    # Keep short resume-note aligned for older readers.
    next_action = str(state.get("next_action") or state.get("next_step") or "(none)").strip()
    resume_note = path.parent / "resume-note.md"
    resume_note.write_text(
        "# Resume Note\n\n"
        f"Last: {_clip(summary or state.get('active_task') or 'No summary.', 300)}\n\n"
        f"Next: {_clip(next_action, 300)}\n\n"
        f"Portable: {REL_PATH.as_posix()}\n",
        encoding="utf-8",
    )
    return {
        "written": True,
        "skipped": False,
        "path": str(path),
        "bytes": len(text.encode("utf-8")),
        "schema": SCHEMA,
    }


def read_portable_handoff(repo_root: Path) -> str:
    path = portable_path(repo_root)
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def inject_summary(repo_root: Path, max_chars: int = 700) -> str:
    """Short SessionStart block: Goal / Next / path. Docs: SessionStart additionalContext."""
    text = read_portable_handoff(repo_root)
    if not text:
        return ""
    goal = ""
    next_step = ""
    session_id = ""
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if line.startswith("schema:") or line.startswith("updated_at:") or line.startswith("project_root:"):
            continue
        if section == "goal" and line.strip() and not line.startswith("#"):
            if not goal:
                goal = line.strip()
        elif section == "next step" and line.strip() and not line.startswith("#"):
            if not next_step:
                next_step = line.strip()
        elif section == "where" and line.strip().startswith("- session_id:"):
            session_id = line.split(":", 1)[-1].strip()
    goal = _clip(goal, 200)
    next_step = _clip(next_step, 200)
    if not goal and not next_step:
        return ""
    out = [
        "Portable handoff (any tool/model — read full file for plan+memory):",
        f"  path: {REL_PATH.as_posix()}",
    ]
    if goal:
        out.append(f"  Goal: {goal}")
    if next_step:
        out.append(f"  Next: {next_step}")
    if session_id and session_id != "none":
        out.append(
            f"  Codex native: try `codex resume {session_id}` or app-server thread/resume "
            "before starting from scratch."
        )
    else:
        out.append(
            "  Codex native: if same chat, try `codex resume --last` "
            "(or app-server thread/resume) before re-deriving."
        )
    block = "\n".join(out)
    if len(block) > max_chars:
        return block[: max_chars - 3] + "..."
    return block


def main() -> None:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="ACC portable handoff writer/reader")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--read", action="store_true")
    parser.add_argument("--inject", action="store_true")
    parser.add_argument("--tool-left", default="codex")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if args.inject:
        print(inject_summary(root))
        return
    if args.read:
        print(read_portable_handoff(root), end="")
        return
    # default write
    result = write_portable_handoff(
        root,
        tool_left=args.tool_left,
        session_id=args.session_id,
        summary=args.summary,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
