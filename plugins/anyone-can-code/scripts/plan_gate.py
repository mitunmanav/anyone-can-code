#!/usr/bin/env python3
"""Plan gate: require a stepped PLAN.md before product file writes.

Skill-first. Soft PreToolUse hint only when preferences.plan_gate_required.
Never hard-deny by default (hook risk).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

NAMESPACE = Path(".codex") / "anyone-can-code"
PLAN_REL = NAMESPACE / "artifacts" / "PLAN.md"
DEFAULT_MAX_AGE_HOURS = 72.0

# Codex apply_patch path lines + simple Edit/Write path keys.
_FILE_LINE_RE = re.compile(
    r"(?:\*\*\*\s+)?(?:Update|Add|Delete|Move)\s+File:\s*([^\n]+)",
    re.IGNORECASE,
)
_STEP_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+\S+",
    re.MULTILINE,
)
_PRODUCT_TOOLS = frozenset({"apply_patch", "edit", "write"})


def plan_path(repo_root: Path) -> Path:
    return Path(repo_root) / PLAN_REL


def extract_steps(text: str) -> list[str]:
    """Return bullet/numbered plan steps from markdown-ish text."""
    steps: list[str] = []
    for match in _STEP_RE.finditer(text or ""):
        line = match.group(0).strip()
        # Drop pure decoration lines
        if line in {"-", "*", "+"}:
            continue
        steps.append(line)
    return steps


def _age_hours(path: Path, *, now: float | None) -> float | None:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    clock = time.time() if now is None else float(now)
    return max(0.0, (clock - mtime) / 3600.0)


def assess_plan(
    repo_root: Path,
    *,
    now: float | None = None,
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
) -> dict[str, Any]:
    """Check plan artifact. status: ok | missing | empty | no_steps | stale."""
    path = plan_path(repo_root)
    rel = str(PLAN_REL).replace("\\", "/")
    base: dict[str, Any] = {
        "path": rel,
        "absolute_path": str(path),
        "exists": False,
        "status": "missing",
        "can_write_product": False,
        "step_count": 0,
        "steps": [],
        "age_hours": None,
        "max_age_hours": float(max_age_hours),
        "message": "No plan. Run $plan-gate or $plan. Write steps to .codex/anyone-can-code/artifacts/PLAN.md. Wait for user GO before product writes.",
        "rule": "plan-before-write: product writes need PLAN.md with steps",
    }
    if not path.is_file():
        return base

    base["exists"] = True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        base["status"] = "missing"
        base["message"] = "Plan file unreadable. Rewrite PLAN.md with steps."
        return base

    if not text.strip():
        base["status"] = "empty"
        base["message"] = "PLAN.md empty. Add ordered steps, then ask user GO."
        return base

    steps = extract_steps(text)
    base["steps"] = steps[:40]
    base["step_count"] = len(steps)
    age = _age_hours(path, now=now)
    base["age_hours"] = None if age is None else round(age, 2)

    if not steps:
        base["status"] = "no_steps"
        base["message"] = (
            "PLAN.md has no list steps. Add bullets or numbered steps before product writes."
        )
        return base

    if age is not None and age > float(max_age_hours):
        base["status"] = "stale"
        base["message"] = (
            f"Plan stale ({base['age_hours']}h > {max_age_hours}h). "
            "Refresh PLAN.md with current steps, then GO."
        )
        return base

    base["status"] = "ok"
    base["can_write_product"] = True
    base["message"] = f"Plan ok ({len(steps)} steps). Product writes allowed after user GO."
    return base


def _is_acc_runtime_path(raw: str) -> bool:
    n = raw.replace("\\", "/").strip().lower()
    if not n:
        return False
    if ".codex/anyone-can-code/" in n:
        return True
    # Bare PLAN.md under ACC artifacts common short form
    if n.endswith("artifacts/plan.md") and "anyone-can-code" in n:
        return True
    return False


def _tool_blob(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        parts: list[str] = []
        for key in ("command", "path", "file_path", "filePath", "content"):
            val = tool_input.get(key)
            if isinstance(val, str) and val.strip():
                parts.append(val)
        if parts:
            return "\n".join(parts)
        return json.dumps(tool_input, ensure_ascii=False)
    if isinstance(tool_input, str):
        return tool_input
    return ""


def is_product_write(tool_name: str, tool_input: Any) -> bool:
    """True when tool is a product file write (not ACC runtime-only)."""
    name = (tool_name or "").strip().lower()
    if name not in _PRODUCT_TOOLS:
        return False
    blob = _tool_blob(tool_input)
    paths = [m.group(1).strip() for m in _FILE_LINE_RE.finditer(blob)]
    if isinstance(tool_input, dict):
        for key in ("path", "file_path", "filePath"):
            val = tool_input.get(key)
            if isinstance(val, str) and val.strip():
                paths.append(val.strip())
    if not paths:
        # apply_patch without parseable paths → treat as product write
        return True
    return any(not _is_acc_runtime_path(p) for p in paths)


def pretool_soft_hint(
    repo_root: Path,
    payload: dict[str, Any],
    prefs: dict[str, Any] | None = None,
    *,
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
) -> str | None:
    """Advisory PreToolUse context when plan_gate_required and plan not ok.

    Soft only — never deny. Skill-first; prefs opt-in.
    """
    prefs = prefs or {}
    if not prefs.get("plan_gate_required"):
        return None
    if (payload.get("hook_event_name") or "") != "PreToolUse":
        return None
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input")
    if not is_product_write(tool_name, tool_input):
        return None
    result = assess_plan(repo_root, max_age_hours=max_age_hours)
    if result.get("can_write_product"):
        return None
    return (
        f"Plan gate: {result.get('message')} "
        "Use $plan-gate (or $plan). No product write until plan steps exist + user GO."
    )


def write_plan_skeleton(
    repo_root: Path,
    *,
    goal: str,
    steps: list[str],
) -> Path:
    """Create/replace PLAN.md with a short stepped plan."""
    path = plan_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    clean_goal = (goal or "Work").strip() or "Work"
    clean_steps = [s.strip() for s in steps if str(s).strip()]
    if not clean_steps:
        clean_steps = ["Clarify scope", "Implement", "Verify"]
    lines = [
        "# Plan",
        "",
        f"Goal: {clean_goal}",
        "",
        "## Steps",
        "",
    ]
    for i, step in enumerate(clean_steps, start=1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("Rule: wait for user GO before product file writes.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ACC plan gate: check PLAN.md artifact")
    parser.add_argument(
        "--repo",
        default=".",
        help="Repo root (default: cwd)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON assessment",
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=DEFAULT_MAX_AGE_HOURS,
        help=f"Stale after this many hours (default {DEFAULT_MAX_AGE_HOURS})",
    )
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    result = assess_plan(repo, max_age_hours=args.max_age_hours)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"status={result['status']} can_write={result['can_write_product']}")
        print(result["message"])
    return 0 if result.get("can_write_product") else 1


if __name__ == "__main__":
    sys.exit(main())
