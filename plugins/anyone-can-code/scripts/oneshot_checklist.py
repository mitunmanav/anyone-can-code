#!/usr/bin/env python3
"""Strong one-shot checklist: plan → build → verify → done.

Pure state machine for $oneshot / $strong-run. Fail hard on skip.
No "done" without verify evidence recorded this run.
Optional thin write to progress-ledger.md.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

PHASES = ("plan", "build", "verify", "done")
_PHASE_INDEX = {name: i for i, name in enumerate(PHASES)}

STATE_REL = Path(".codex") / "anyone-can-code" / "state" / "oneshot.json"
LEDGER_REL = Path(".codex") / "anyone-can-code" / "state" / "progress-ledger.md"
PLAN_REL = Path(".codex") / "anyone-can-code" / "artifacts" / "PLAN.md"


class OneshotError(Exception):
    """Illegal phase skip or missing verify evidence."""


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def state_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / STATE_REL


def plan_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / PLAN_REL


def ledger_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / LEDGER_REL


def _empty(goal: str = "") -> dict[str, Any]:
    return {
        "goal": (goal or "").strip(),
        "phase": "plan",
        "completed": [],
        "notes": {},
        "evidence": {},
        "ok_to_claim_done": False,
        "updated": _utc_now(),
    }


def load_state(repo_root: Path | str) -> dict[str, Any]:
    path = state_path(repo_root)
    if not path.is_file():
        return _empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty()
    if not isinstance(data, dict):
        return _empty()
    base = _empty(str(data.get("goal") or ""))
    base["phase"] = data.get("phase") if data.get("phase") in PHASES else "plan"
    completed = data.get("completed") or []
    base["completed"] = [p for p in completed if p in PHASES]
    notes = data.get("notes") or {}
    base["notes"] = notes if isinstance(notes, dict) else {}
    evidence = data.get("evidence") or {}
    base["evidence"] = evidence if isinstance(evidence, dict) else {}
    base["ok_to_claim_done"] = bool(
        base["evidence"].get("verify") and "verify" in base["completed"]
    )
    base["updated"] = str(data.get("updated") or base["updated"])
    return base


def save_state(repo_root: Path | str, state: dict[str, Any]) -> Path:
    path = state_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = dict(state)
    state["updated"] = _utc_now()
    state["ok_to_claim_done"] = bool(
        state.get("evidence", {}).get("verify") and "verify" in (state.get("completed") or [])
    )
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def init_run(repo_root: Path | str, goal: str) -> dict[str, Any]:
    """Start a new strong one-shot at plan."""
    clean = (goal or "").strip() or "one focused goal"
    state = _empty(clean)
    save_state(repo_root, state)
    return load_state(repo_root)


def status(repo_root: Path | str) -> dict[str, Any]:
    return load_state(repo_root)


def assert_can_claim_done(repo_root: Path | str) -> None:
    state = load_state(repo_root)
    if not state.get("ok_to_claim_done"):
        raise OneshotError(
            "No done without verify evidence this run. "
            "Advance verify with --evidence (fresh command output), then done."
        )


def advance(
    repo_root: Path | str,
    phase: str,
    *,
    note: str = "",
    evidence: str | None = None,
) -> dict[str, Any]:
    """Mark `phase` complete. Must match current phase; no skips."""
    name = (phase or "").strip().lower()
    if name not in _PHASE_INDEX:
        raise OneshotError(f"Unknown phase {phase!r}. Use: {', '.join(PHASES)}")

    state = load_state(repo_root)
    if not state.get("goal"):
        raise OneshotError("No oneshot run. Call init first.")

    current = state["phase"]
    if name != current:
        raise OneshotError(
            f"Illegal skip: expected {current}, got {name}. "
            f"Complete phases in order: plan → build → verify → done."
        )

    if name == "verify":
        ev = (evidence if evidence is not None else "").strip()
        if not ev:
            raise OneshotError(
                "Verify needs fresh evidence (command + result). "
                "No empty evidence. No done without verify evidence."
            )
        state.setdefault("evidence", {})["verify"] = ev[:2000]

    if note and note.strip():
        state.setdefault("notes", {})[name] = note.strip()[:500]

    completed = list(state.get("completed") or [])
    if name not in completed:
        completed.append(name)
    state["completed"] = completed

    idx = _PHASE_INDEX[name]
    if name == "done":
        assert_can_claim_done_state(state)
        state["phase"] = "done"
    else:
        state["phase"] = PHASES[idx + 1]

    save_state(repo_root, state)
    return load_state(repo_root)


def assert_can_claim_done_state(state: dict[str, Any]) -> None:
    if not (state.get("evidence") or {}).get("verify"):
        raise OneshotError(
            "No done without verify evidence this run. "
            "Record verify evidence before claiming done."
        )
    if "verify" not in (state.get("completed") or []):
        raise OneshotError("Verify phase not completed. Cannot claim done.")


def status_card(repo_root: Path | str) -> str:
    state = load_state(repo_root)
    done_flag = "YES" if state.get("ok_to_claim_done") else "NO"
    completed = ", ".join(state.get("completed") or []) or "(none)"
    lines = [
        "WHERE: oneshot / strong-run",
        f"GOAL: {state.get('goal') or '(none)'}",
        f"PHASE: {state.get('phase')}",
        f"COMPLETED: {completed}",
        f"DONE?: {done_flag} (need verify evidence)",
    ]
    ev = (state.get("evidence") or {}).get("verify")
    if ev:
        lines.append(f"EVIDENCE: {ev[:240]}")
    next_map = {
        "plan": "Write PLAN.md steps, then advance plan",
        "build": "TDD implement, then advance build",
        "verify": "Run $verify fresh; advance verify --evidence ...",
        "done": "Status card. Stop. Back to normal.",
    }
    lines.append(f"NEXT: {next_map.get(state.get('phase', ''), 'status')}")
    return "\n".join(lines)


def touch_ledger(
    repo_root: Path | str,
    *,
    where: str,
    next_step: str,
    done_item: str | None = None,
) -> Path:
    """Simple progress-ledger.md write (optional helper)."""
    path = ledger_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    where_s = (where or "").strip() or "oneshot"
    next_s = (next_step or "").strip() or "continue oneshot chain"
    done_lines = [f"- [x] {done_item.strip()}"] if done_item and done_item.strip() else []
    if path.is_file():
        try:
            old = path.read_text(encoding="utf-8")
        except OSError:
            old = ""
        # Keep prior DONE bullets if present
        if "## DONE" in old and not done_lines:
            section = old.split("## DONE", 1)[1]
            rest = section.split("## ", 1)[0]
            for line in rest.splitlines():
                s = line.strip()
                if s.startswith("-"):
                    done_lines.append(s)
    body = [
        "# Progress ledger",
        "",
        f"Updated: {_utc_now()}",
        "",
        "## WHERE",
        where_s,
        "",
        "## NEXT",
        next_s,
        "",
        "## DONE",
    ]
    body.extend(done_lines or ["- (none yet)"])
    body.extend(["", "## OPEN", "- (none)", ""])
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC strong one-shot checklist (plan|build|verify|done)."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: cwd)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Start oneshot at plan")
    p_init.add_argument("--goal", required=True, help="One focused goal")

    p_adv = sub.add_parser("advance", help="Complete current phase")
    p_adv.add_argument("phase", choices=list(PHASES))
    p_adv.add_argument("--note", default="", help="Short note for this phase")
    p_adv.add_argument(
        "--evidence",
        default=None,
        help="Required for verify: fresh command + result",
    )

    p_status = sub.add_parser("status", help="Show state")
    p_status.add_argument("--json", action="store_true")
    p_status.add_argument("--card", action="store_true", help="Print status card")

    p_done = sub.add_parser("check-done", help="Exit 0 only if verify evidence exists")

    p_ledger = sub.add_parser("ledger", help="Optional progress-ledger write")
    p_ledger.add_argument("--where", required=True)
    p_ledger.add_argument("--next", dest="next_step", required=True)
    p_ledger.add_argument("--done", dest="done_item", default=None)

    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    try:
        if args.cmd == "init":
            state = init_run(repo, args.goal)
            print(json.dumps(state, indent=2))
            return 0
        if args.cmd == "advance":
            state = advance(
                repo,
                args.phase,
                note=args.note or "",
                evidence=args.evidence,
            )
            print(json.dumps(state, indent=2))
            return 0
        if args.cmd == "status":
            if args.card:
                print(status_card(repo))
            elif args.json:
                print(json.dumps(status(repo), indent=2))
            else:
                s = status(repo)
                print(
                    f"phase={s['phase']} done={s['ok_to_claim_done']} goal={s.get('goal')}"
                )
            return 0
        if args.cmd == "check-done":
            assert_can_claim_done(repo)
            print("ok_to_claim_done=true")
            return 0
        if args.cmd == "ledger":
            path = touch_ledger(
                repo,
                where=args.where,
                next_step=args.next_step,
                done_item=args.done_item,
            )
            print(str(path))
            return 0
    except OneshotError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
