"""
Load small session context.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_core
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
try:
    import cross_agent_pack as _cross_agent_pack
except Exception:  # pragma: no cover
    _cross_agent_pack = None


def read_agents_md(repo_root: Path) -> str:
    path = repo_root / "AGENTS.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")[:2000]
        except OSError:
            return ""
    return ""


MEMORY_RECALL_CHAR_CAP = 1200
MEMORY_RECALL_KINDS = {"lesson", "mistake", "correction", "failure", "want", "decision"}
MEMORY_BLOCK_CHAR_CAP = 1500


def build_memory_block(repo_root: Path, source: str) -> str:
    """Constant-size memory inject: NOW facts first, crash flag, top lessons.
    Total never exceeds MEMORY_BLOCK_CHAR_CAP no matter how big the store is."""
    workflow = state.read_state(repo_root)
    lines = ["NOW:"]
    goal = workflow.get("active_goal") or workflow.get("active_task")
    if goal:
        lines.append(f"  Goal: {str(goal)[:240]}")
    lines.append(f"  Next: {str(workflow.get('next_step') or 'N/A')[:240]}")
    decision = workflow.get("last_decision")
    if decision:
        lines.append(f"  Last decision: {str(decision)[:200]}")
    if workflow.get("turn_status") == "open" and source in {"startup", "resume"}:
        ask = str(workflow.get("open_ask") or "")[:200]
        if ask:
            lines.append(f"  CRASH RESUME: last request may be unfinished: {ask}")
    block = "\n".join(lines)
    return block[:MEMORY_BLOCK_CHAR_CAP]


def recall_wiki_brief(repo_root: Path) -> str:
    """Karpathy index-first brief. Never touches Codex native memories."""
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import wiki_memory as _wiki_memory  # type: ignore

        memory_root = state.ensure_project_layout(repo_root)["memory"]
        return _wiki_memory.session_brief(memory_root)
    except Exception:
        return ""


def recall_memory_notes(repo_root: Path) -> tuple[list[str], str]:
    """Read active lesson notes from every scope folder; strongest first. Cap size."""
    layout = state.ensure_project_layout(repo_root)
    notes_dir = layout["memory"] / "notes"
    if not notes_dir.exists():
        return [], ""
    note_files = list(notes_dir.rglob("*.md")) if notes_dir.exists() else []
    if len(note_files) > 50:
        try:
            import memory_index
            workflow = state.read_state(repo_root)
            query = " ".join(filter(None, [
                str(workflow.get("active_goal") or ""),
                str(workflow.get("next_step") or "")]))[:200]
            hits = memory_index.search(layout["memory"], query, limit=5)
            if hits:
                lessons = [f"- {h['summary'][:160]}" for h in hits]
                proof = f"{state.utc_now()} recalled {len(lessons)} lesson(s) via index"
                return lessons, proof
        except Exception:
            pass  # fall through to the direct scan
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


def build_context(
    repo_root: Path,
    source: str,
    *,
    session_id: str | None = None,
) -> str:
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
    wiki_brief = recall_wiki_brief(repo_root)
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
    context_lines.append(build_memory_block(repo_root, source))
    reasoning = rec.get("reasoning") or "medium"
    context_lines += [
        f"State: {workflow.get('phase', 'idle')} / {workflow.get('route', 'unknown')}.",
        f"Next: {workflow.get('next_step', 'N/A')}.",
        f"ENFORCE comm rule: {comm_mode}. Short replies only. No walls of text.",
        f"Memory: {workflow.get('memory_mode', 'portable-markdown')}. "
        "Project drawer: .codex/anyone-can-code/memory/. "
        "User taste: ~/.codex/anyone-can-code/user-memory/. "
        "Native Codex /memories OFF for ACC project notes.",
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
        "Proof: never claim done/works/perfect without named evidence. Built ≠ verified.",
    ]
    # Live product paths for scripts that used to be test-only helpers.
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import host_detect as _host_detect

        guide = _host_detect.host_guidance()
        context_lines.append(
            f"Host: {guide.get('host', 'unknown')}. {guide.get('review', '')}"
        )
    except Exception:
        pass
    # PLUGIN_ROOT is hook-only (Codex hooks docs). Inject real path so skills
    # can run scripts without assuming the agent shell has PLUGIN_ROOT.
    acc_plugin_root = (
        os.environ.get("PLUGIN_ROOT")
        or os.environ.get("CLAUDE_PLUGIN_ROOT")
        or str(Path(__file__).resolve().parents[2])
    )
    context_lines.append(
        f"ACC_PLUGIN_ROOT={acc_plugin_root}. "
        "Run scripts: python3 \"{0}/scripts/<name>.py\". "
        "PLUGIN_ROOT is hooks-only; agent shell uses this path.".format(acc_plugin_root)
    )
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import loop_registry as _loop_registry

        # Real product call: inject live loop status from list_loops(), not a
        # discarded import-proof. Full menu stays available via CLI / $status.
        loops = _loop_registry.list_loops()
        bits = []
        for loop in loops:
            lid = str(loop.get("id") or "")
            if not lid:
                continue
            if loop.get("opt_in"):
                bits.append(f"{lid}=opt-in")
            else:
                bits.append(f"{lid}=on")
        if bits:
            context_lines.append(
                "Loops: " + ", ".join(bits) + ". "
                + _loop_registry.plain_menu().splitlines()[0]
            )
    except Exception:
        pass
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import ai_observability as _ai_obs

        receipt = _ai_obs.build_plain_receipt(repo_root, limit=3)
        if receipt.get("count"):
            context_lines.append(str(receipt.get("user_block") or "")[:240])
        else:
            context_lines.append("What AI did: nothing recorded yet this project.")
    except Exception:
        pass
    if _cross_agent_pack is not None:
        try:
            context_lines.append(_cross_agent_pack.env_agent_line())
        except Exception:
            pass
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
    # Portable handoff inject (docs: SessionStart additionalContext; any tool can open the file).
    try:
        scripts = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import portable_handoff as _portable_handoff  # type: ignore

        portable_block = _portable_handoff.inject_summary(repo_root)
        if portable_block:
            context_lines.append(portable_block)
    except Exception:
        pass
    if wiki_brief:
        context_lines.append(wiki_brief)
    if memory_lines:
        context_lines.append("Memory recall (apply these lessons):")
        context_lines.extend(f"  {line}" for line in memory_lines)
    if _rate_limit_guard is not None:
        try:
            for line in _rate_limit_guard.build_guard_lines(session_id=session_id):
                context_lines.append(line)
        except Exception:
            pass
    if agents:
        context_lines.append("")
        context_lines.append("Project rules:")
        context_lines.append(agents)
    return "\n".join(context_lines)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    try:
        memory_core.write_heartbeat(state.ensure_project_layout(repo_root)["memory"])
    except Exception:
        pass
    source = payload.get("source", "startup")
    session_id = str(payload.get("session_id") or "") or None
    ctx = build_context(repo_root, source, session_id=session_id)
    if not _first_run.is_configured(repo_root):
        ctx += (
            "\n\nFIRST RUN: Ask user one question only: non-tech, middle, or developer "
            "(or builder/mixed/developer)? Then call $setup. Also ask: set up automations? "
            "Default NO."
        )
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
