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

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"

# Soft inject budget: Tier A always; B then C if room. Lean skips C.
SESSION_CONTEXT_SOFT_CAP = 5500


def _ensure_scripts_path() -> None:
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))


def _lazy_import(name: str):
    """Import hook-local or scripts module only when needed."""
    hook_local = {
        "first_run",
        "model_ledger",
        "version_check",
        "rule_promote",
        "user_model",
        "capabilities",
    }
    if name not in hook_local:
        _ensure_scripts_path()
    return __import__(name)


def _load_full_tier_c() -> bool:
    """Tier C on by default; ACC_LOAD_LEAN=1 skips host/loops/obs parade."""
    return os.environ.get("ACC_LOAD_LEAN", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }

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
    """Session inject: Tier A always; B then C if under soft cap; lean skips C."""
    workflow = state.read_state(repo_root)
    prefs = state.read_preferences(repo_root)
    agents = read_agents_md(repo_root)
    task_type = workflow.get("route") or "general"
    comm_mode = prefs.get("communication_mode", "caveman-strict")

    # --- Tier A: always (smart core) ---
    mistake_lines: list[str] = []
    try:
        mistakes = state.read_recent_jsonl(state.mistake_log_path(repo_root), limit=5)
        for m in mistakes[-3:]:
            detail = m.get("detail") or m.get("signal_type", "unknown")
            mistake_lines.append(f"  - {detail}")
    except Exception:
        pass

    tier_a: list[str] = [
        "Style: strict caveman. Short. Direct. No filler. Re-read this every turn."
    ]
    if source == "compact":
        tier_a.append(
            "Context was compacted. Re-anchor on the state below; "
            "do not re-ask answered questions."
        )
    tier_a.append(build_memory_block(repo_root, source))
    tier_a += [
        f"State: {workflow.get('phase', 'idle')} / {workflow.get('route', 'unknown')}.",
        f"Next: {workflow.get('next_step', 'N/A')}.",
        f"ENFORCE comm rule: {comm_mode}. Short replies only. No walls of text.",
        f"Memory: {workflow.get('memory_mode', 'portable-markdown')}. "
        "Project drawer: .codex/anyone-can-code/memory/. "
        "User taste: ~/.codex/anyone-can-code/user-memory/. "
        "Native Codex /memories OFF for ACC project notes.",
        f"From: {source}.",
        (
            "Session end rule: before stopping, give a 3-line recap — "
            "1) what got done, 2) what is next, 3) what the user must decide. "
            "Never stop on an unanswered question from the user."
        ),
        "Skills: use progressive load; do not re-read every skill file each turn.",
        "Proof: never claim done/works/perfect without named evidence. Built ≠ verified.",
        "Cost: label suggestions [CHEAP] or [HUNGRY]. Prefer cheap first.",
    ]
    acc_plugin_root = (
        os.environ.get("PLUGIN_ROOT")
        or os.environ.get("CLAUDE_PLUGIN_ROOT")
        or str(Path(__file__).resolve().parents[2])
    )
    tier_a.append(
        f"ACC_PLUGIN_ROOT={acc_plugin_root}. "
        'Run scripts: python3 "{0}/scripts/<name>.py". '
        "PLUGIN_ROOT is hooks-only; agent shell uses this path.".format(acc_plugin_root)
    )
    if mistake_lines:
        tier_a.append("Recent mistakes (do not repeat):")
        tier_a.extend(mistake_lines)

    context_lines = list(tier_a)
    used = len("\n".join(context_lines))

    def _room(extra: int = 80) -> bool:
        return used + extra < SESSION_CONTEXT_SOFT_CAP

    def _add(line: str) -> None:
        nonlocal used
        if not line:
            return
        if used + len(line) + 1 > SESSION_CONTEXT_SOFT_CAP:
            return
        context_lines.append(line)
        used += len(line) + 1

    # --- Tier B: memory + model + rules (lazy imports) ---
    if _room(200):
        memory_lines, read_proof = recall_memory_notes(repo_root)
        wiki_brief = recall_wiki_brief(repo_root)
        if read_proof:
            try:
                state.write_state(repo_root, {"memory_read_proof": read_proof})
            except Exception:
                pass
        try:
            _model_ledger = _lazy_import("model_ledger")
            ledger_path = (
                state.ensure_project_layout(repo_root)["state"] / "model-ledger.jsonl"
            )
            rec = _model_ledger.recommend_model(task_type, ledger_path=ledger_path)
            reasoning = rec.get("reasoning") or "medium"
            _add(
                f"Model: {rec['model']} reasoning={reasoning} ({rec['reason']}). "
                "Not always high effort."
            )
        except Exception:
            pass
        try:
            rules = _lazy_import("rule_promote").approved_rules(repo_root)
        except Exception:
            rules = []
        if rules and _room():
            _add("Permanent rules (user approved):")
            for rule in rules:
                _add(f"  {rule}")
        try:
            about = _lazy_import("user_model").about_you_line(repo_root)
            if about:
                _add(about)
        except Exception:
            pass
        if wiki_brief:
            _add(wiki_brief)
        if memory_lines:
            _add("Memory recall (apply lessons):")
            for line in memory_lines:
                _add(f"  {line}")
        try:
            _ensure_scripts_path()
            import portable_handoff as _portable_handoff  # type: ignore

            portable_block = _portable_handoff.inject_summary(repo_root)
            if portable_block:
                _add(portable_block)
        except Exception:
            pass
        if agents and _room(len(agents) + 40):
            _add("")
            _add("Project rules:")
            _add(agents)
        # Repo map (optional): thin inject only if artifact exists + cap.
        # Prefs repo_map_inject=false disables. Default = on when present.
        try:
            inject_ok = prefs.get("repo_map_inject", True)
            if inject_ok is not False and _room(120):
                _ensure_scripts_path()
                import repo_map as _repo_map  # type: ignore

                map_snip = _repo_map.inject_snippet(repo_root)
                if map_snip:
                    _add(map_snip)
        except Exception:
            pass

    # --- Tier C: host / loops / obs (lazy; ACC_LOAD_LEAN=1 skips) ---
    if _load_full_tier_c() and _room(100):
        try:
            _ensure_scripts_path()
            import host_detect as _host_detect

            guide = _host_detect.host_guidance()
            _add(f"Host: {guide.get('host', 'unknown')}. {guide.get('review', '')}")
        except Exception:
            pass
        try:
            _ensure_scripts_path()
            import loop_registry as _loop_registry

            loops = _loop_registry.list_loops()
            bits: list[str] = []
            for loop in loops:
                lid = str(loop.get("id") or "")
                if not lid:
                    continue
                if loop.get("opt_in"):
                    bits.append(f"{lid}=opt-in")
                else:
                    bits.append(f"{lid}=on")
            if bits:
                menu0 = _loop_registry.plain_menu().splitlines()[0]
                _add("Loops: " + ", ".join(bits) + ". " + menu0)
        except Exception:
            pass
        try:
            _ensure_scripts_path()
            import ai_observability as _ai_obs

            receipt = _ai_obs.build_plain_receipt(repo_root, limit=3)
            if receipt.get("count"):
                _add(str(receipt.get("user_block") or "")[:240])
            else:
                _add("What AI did: nothing recorded yet for this project.")
        except Exception:
            pass
        try:
            pack = _lazy_import("cross_agent_pack")
            _add(pack.env_agent_line())
        except Exception:
            pass
        try:
            nudge = _lazy_import("version_check").update_nudge()
            if nudge:
                _add(nudge)
        except Exception:
            pass
        try:
            cap_line = _lazy_import("capabilities").capability_line(repo_root)
            if cap_line:
                _add(cap_line)
        except Exception:
            pass
        _add(
            "Observability: after tool work, tell the user what you did "
            "in plain words (What AI did)."
        )

    # Token-burn opt-in only (expensive on Windows)
    if os.environ.get("ACC_TOKEN_BURN", "").strip().lower() in {"1", "true", "yes"}:
        try:
            rlg = _lazy_import("rate_limit_guard")
            for line in rlg.build_guard_lines(session_id=session_id):
                _add(line)
        except Exception:
            pass

    return "\n".join(context_lines)


def handle_payload(payload: dict, repo_root: Path) -> dict:
    try:
        memory_core.write_heartbeat(state.ensure_project_layout(repo_root)["memory"])
    except Exception:
        pass
    source = payload.get("source", "startup")
    session_id = str(payload.get("session_id") or "") or None
    ctx = build_context(repo_root, source, session_id=session_id)
    try:
        _configured = _lazy_import("first_run").is_configured(repo_root)
    except Exception:
        _configured = True
    if not _configured:
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
