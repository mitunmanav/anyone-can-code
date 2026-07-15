"""
Load small session context.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state
import first_run as _first_run
import model_ledger as _model_ledger
import version_check as _version_check
import rule_promote as _rule_promote
import user_model as _user_model
import capabilities as _capabilities

# Cheap rate-limit + token-burn guard (reads ~/.codex/sessions rollout files).
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
try:
    import rate_limit_guard as _rate_limit_guard
except Exception:  # pragma: no cover - optional if scripts path missing
    _rate_limit_guard = None


def read_agents_md(repo_root: Path) -> str:
    path = repo_root / "AGENTS.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")[:2000]
        except OSError:
            return ""
    return ""


MEMORY_RECALL_CHAR_CAP = 1200
MEMORY_RECALL_KINDS = {"lesson", "mistake", "correction", "failure"}


def recall_memory_notes(repo_root: Path) -> tuple[list[str], str]:
    """Read active lesson notes from every scope folder; strongest first. Cap size."""
    layout = state.ensure_project_layout(repo_root)
    notes_dir = layout["memory"] / "notes"
    if not notes_dir.exists():
        return [], ""
    scored: list[tuple[int, str, str]] = []
    for note_file in notes_dir.rglob("*.md"):
        try:
            text = note_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if '"revoked"' in text or "status: revoked" in text or 'status: "revoked"' in text:
            continue
        kind_match = re.search(r'kind:\s*"?(\w+)"?', text)
        if kind_match:
            if kind_match.group(1) not in MEMORY_RECALL_KINDS:
                continue
            summary_match = re.search(r"## Summary\s+(.+?)(?:\n## |\Z)", text, re.S)
            if not summary_match:
                continue
            weight_match = re.search(r"reinforcement_count:\s*(\d+)", text)
            weight = int(weight_match.group(1)) if weight_match else 1
            line = summary_match.group(1).strip().splitlines()[0][:160]
            scored.append((weight, line, note_file.name))
            continue
        # Legacy flat notes (bullet lines, no frontmatter) — still never-repeat.
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                scored.append((1, stripped.lstrip("- ").strip()[:160], note_file.name))
    if not scored:
        return [], ""
    scored.sort(reverse=True)
    lessons: list[str] = []
    used_files: list[str] = []
    total = 0
    for weight, line, name in scored:
        entry = f"- {line}" if not line.startswith("-") else line
        if total + len(entry) > MEMORY_RECALL_CHAR_CAP:
            break
        lessons.append(entry)
        if name not in used_files:
            used_files.append(name)
        total += len(entry)
    proof = f"{state.utc_now()} recalled {len(lessons)} lesson(s) from {', '.join(used_files[:5])}"
    return lessons, proof


def build_context(repo_root: Path, source: str) -> str:
    workflow = state.read_state(repo_root)
    prefs = state.read_preferences(repo_root)
    agents = read_agents_md(repo_root)
    task_type = workflow.get("route") or "general"
    ledger_path = state.ensure_project_layout(repo_root)["state"] / "model-ledger.jsonl"
    rec = _model_ledger.recommend_model(task_type, ledger_path=ledger_path)
    comm_mode = prefs.get("communication_mode", "caveman-strict")

    # Surface recent mistakes
    mistake_lines = []
    try:
        mistakes = state.read_recent_jsonl(state.mistake_log_path(repo_root), limit=5)
        for m in mistakes[-3:]:
            detail = m.get("detail") or m.get("signal_type", "unknown")
            mistake_lines.append(f"  - {detail}")
    except Exception:
        pass

    memory_lines, read_proof = recall_memory_notes(repo_root)
    if read_proof:
        try:
            state.write_state(repo_root, {"memory_read_proof": read_proof})
        except Exception:
            pass

    context_lines = [
        "Style: strict caveman. Short. Direct. No filler. Re-read this every turn."
    ]
    if source == "compact":
        context_lines.append(
            "Context was compacted. Re-anchor on the state below; do not re-ask answered questions."
        )
    goal = workflow.get("active_goal") or workflow.get("active_task")
    if goal:
        context_lines.append(f"Goal: {str(goal)[:240]}")
    reasoning = rec.get("reasoning") or "medium"
    context_lines += [
        f"State: {workflow.get('phase', 'idle')} / {workflow.get('route', 'unknown')}.",
        f"Next: {workflow.get('next_step', 'N/A')}.",
        f"ENFORCE comm rule: {comm_mode}. Short replies only. No walls of text.",
        f"Memory: {workflow.get('memory_mode', 'portable-markdown')}. ACC two-drawer; native Codex memories OFF.",
        f"From: {source}.",
        f"Model: {rec['model']} reasoning={reasoning} ({rec['reason']}). Not always high effort.",
        (
            "Session end rule: before stopping, give a 3-line recap — "
            "1) what got done, 2) what is next, 3) what the user must decide. "
            "Never stop on an unanswered question from the user."
        ),
        "Observability: after tool work, tell the user what you did in plain words (What AI did).",
        "Cost: label suggestions [CHEAP] or [HUNGRY]. Prefer cheap first.",
        # Item 19: do NOT bulk-load skill bodies here — Codex progressive disclosure does that.
        "Skills: use progressive load; do not re-read every skill file each turn.",
    ]
    try:
        nudge = _version_check.update_nudge()
        if nudge:
            context_lines.append(nudge)
    except Exception:
        pass
    try:
        cap = _capabilities.capability_line(repo_root)
        if cap:
            context_lines.append(cap)
    except Exception:
        pass
    try:
        about = _user_model.about_you_line(repo_root)
        if about:
            context_lines.append(about)
    except Exception:
        pass
    try:
        rules = _rule_promote.approved_rules(repo_root)
    except Exception:
        rules = []
    if rules:
        context_lines.append("Permanent rules (user approved):")
        context_lines.extend(f"  {rule}" for rule in rules)
    if mistake_lines:
        context_lines.append("Recent mistakes (do not repeat):")
        context_lines.extend(mistake_lines)
    if memory_lines:
        context_lines.append("Memory recall (apply these lessons):")
        context_lines.extend(f"  {line}" for line in memory_lines)
    if _rate_limit_guard is not None:
        try:
            for line in _rate_limit_guard.build_guard_lines():
                context_lines.append(line)
        except Exception:
            pass
    if agents:
        context_lines.append("")
        context_lines.append("Project rules:")
        context_lines.append(agents)
    return "\n".join(context_lines)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    source = payload.get("source", "startup")
    ctx = build_context(repo_root, source)
    if not _first_run.is_configured(repo_root):
        ctx += "\n\nFIRST RUN: Ask user one question only: builder, developer, or mixed? Then call $setup."
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
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
