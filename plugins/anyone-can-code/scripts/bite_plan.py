#!/usr/bin/env python3
"""Bite plan: format 2–5 min checkbox steps → artifacts/BITE_PLAN.md.

Superpowers-style bite-sized tasks (one action, 2–5 minutes).
GSD-style small checkable units fight context rot.
Pure helper for $bite-plan. No network.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

NAMESPACE = Path(".codex") / "anyone-can-code"
BITE_REL = NAMESPACE / "artifacts" / "BITE_PLAN.md"

MIN_MINUTES = 2
MAX_MINUTES = 5
DEFAULT_MINUTES = 3

_CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.*)$")
# Matches trailing "~3 min", "(~3 min)", "`(~3 min)`", etc.
_MINUTES_TAIL_RE = re.compile(
    r"\s*[`(]*\(?\s*~?\s*(\d+)\s*min(?:utes?)?\s*\)?[`)]*\s*$",
    re.I,
)
_STEP_NUM_RE = re.compile(r"^\*\*(\d+)\.\*\*\s*")
_LEADING_NUM_RE = re.compile(r"^\d+[.)]\s+")


def bite_plan_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / BITE_REL


def clamp_minutes(value: Any) -> int:
    if value is None or value == "":
        return DEFAULT_MINUTES
    try:
        n = int(float(value))
    except (TypeError, ValueError):
        return DEFAULT_MINUTES
    return max(MIN_MINUTES, min(MAX_MINUTES, n))


def _strip_checkbox_prefix(text: str) -> tuple[str, bool | None]:
    raw = str(text or "").strip()
    match = _CHECKBOX_RE.match(raw)
    if match:
        done = match.group(1).lower() == "x"
        return match.group(2).strip(), done
    # Bare [x]/[ ] prefix without bullet
    if raw.lower().startswith("[x]"):
        return raw[3:].strip(), True
    if raw.startswith("[ ]"):
        return raw[3:].strip(), False
    return raw, None


def _extract_minutes(text: str) -> tuple[str, int | None]:
    match = _MINUTES_TAIL_RE.search(text)
    if not match:
        return text.strip(), None
    minutes = int(match.group(1))
    cleaned = text[: match.start()].rstrip()
    return cleaned, minutes


def normalize_step(step: Any) -> dict[str, Any]:
    """Normalize free text or dict into {text, minutes, done}."""
    done: bool | None = None
    minutes: Any = None
    text = ""

    if isinstance(step, dict):
        text = str(step.get("text") or step.get("step") or step.get("title") or "").strip()
        minutes = step.get("minutes", step.get("mins", step.get("estimate")))
        if "done" in step or "completed" in step:
            done = bool(step.get("done") or step.get("completed"))
    else:
        text = str(step or "").strip()

    text, cb_done = _strip_checkbox_prefix(text)
    if done is None and cb_done is not None:
        done = cb_done
    text, tail_mins = _extract_minutes(text)
    if minutes is None and tail_mins is not None:
        minutes = tail_mins
    text = _STEP_NUM_RE.sub("", text)
    text = _LEADING_NUM_RE.sub("", text).strip()
    # Drop leftover bold wrappers around empty
    text = text.strip("* ").strip()
    if not text:
        text = "Do next small action"

    return {
        "text": text,
        "minutes": clamp_minutes(minutes),
        "done": bool(done),
    }


def build_markdown(
    goal: str,
    steps: list[Any],
    *,
    architecture: str = "",
    tech_stack: str = "",
) -> str:
    """Render Superpowers-style bite plan with checkbox steps."""
    clean_goal = (goal or "Work").strip() or "Work"
    normalized = [normalize_step(s) for s in steps if str(s).strip() or isinstance(s, dict)]
    if not normalized:
        normalized = [
            normalize_step("Write failing test for the change"),
            normalize_step("Implement minimal code to pass"),
            normalize_step("Run tests and confirm green"),
        ]

    lines: list[str] = [
        f"# Bite plan: {clean_goal}",
        "",
        "> 2–5 min steps. One action each. Checkbox tracking. TDD when code.",
        "> Small bites fight context rot — finish and check off before the next.",
        "",
        f"**Goal:** {clean_goal}",
    ]
    arch = (architecture or "").strip()
    if arch:
        lines.append(f"**Architecture:** {arch}")
    stack = (tech_stack or "").strip()
    if stack:
        lines.append(f"**Tech stack:** {stack}")

    lines.extend(["", "## Steps", ""])
    for i, step in enumerate(normalized, start=1):
        mark = "x" if step["done"] else " "
        mins = step["minutes"]
        lines.append(f"- [{mark}] **{i}.** {step['text']} `(~{mins} min)`")

    total = sum(s["minutes"] for s in normalized)
    open_n = sum(1 for s in normalized if not s["done"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Steps: {len(normalized)} ({open_n} open)",
            f"- Estimate: ~{total} min total (each step {MIN_MINUTES}–{MAX_MINUTES})",
            "",
            "## Rules",
            "",
            f"- One action per step ({MIN_MINUTES}–{MAX_MINUTES} minutes).",
            "- Prefer TDD: failing test → minimal code → re-run → check off.",
            "- Mark `[x]` only after verification for that step.",
            "- Wait for user GO before product file writes (if plan-gate on).",
            "",
        ]
    )
    return "\n".join(lines)


def write_bite_plan(
    repo_root: Path,
    *,
    goal: str,
    steps: list[Any],
    architecture: str = "",
    tech_stack: str = "",
) -> Path:
    path = bite_plan_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    md = build_markdown(
        goal,
        steps,
        architecture=architecture,
        tech_stack=tech_stack,
    )
    path.write_text(md, encoding="utf-8")
    return path


def parse_steps(text: str) -> list[dict[str, Any]]:
    """Extract checkbox steps from bite-plan markdown."""
    steps: list[dict[str, Any]] = []
    for line in (text or "").splitlines():
        match = _CHECKBOX_RE.match(line)
        if not match:
            continue
        done = match.group(1).lower() == "x"
        body = match.group(2).strip()
        body, mins = _extract_minutes(body)
        body = _STEP_NUM_RE.sub("", body).strip()
        body = body.strip("* ").strip()
        if not body:
            continue
        steps.append(
            {
                "text": body,
                "minutes": clamp_minutes(mins if mins is not None else DEFAULT_MINUTES),
                "done": done,
            }
        )
    return steps


def assess_bite_plan(repo_root: Path) -> dict[str, Any]:
    """status: ok | missing | empty | no_steps."""
    path = bite_plan_path(repo_root)
    rel = str(BITE_REL).replace("\\", "/")
    base: dict[str, Any] = {
        "path": rel,
        "absolute_path": str(path),
        "exists": False,
        "status": "missing",
        "step_count": 0,
        "open_count": 0,
        "done_count": 0,
        "steps": [],
        "message": (
            "No bite plan. Run $bite-plan. Write 2–5 min checkbox steps to "
            ".codex/anyone-can-code/artifacts/BITE_PLAN.md."
        ),
        "rule": "bite-plan: micro steps 2–5 min with - [ ] checkboxes",
    }
    if not path.is_file():
        return base

    base["exists"] = True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        base["status"] = "missing"
        base["message"] = "BITE_PLAN.md unreadable. Rewrite with checkbox steps."
        return base

    if not text.strip():
        base["status"] = "empty"
        base["message"] = "BITE_PLAN.md empty. Add 2–5 min checkbox steps."
        return base

    steps = parse_steps(text)
    base["steps"] = steps[:80]
    base["step_count"] = len(steps)
    base["done_count"] = sum(1 for s in steps if s["done"])
    base["open_count"] = sum(1 for s in steps if not s["done"])

    if not steps:
        base["status"] = "no_steps"
        base["message"] = (
            "BITE_PLAN.md has no checkbox steps. Add lines like: "
            "- [ ] **1.** Do one small action `(~3 min)`"
        )
        return base

    base["status"] = "ok"
    base["message"] = (
        f"Bite plan ok ({base['step_count']} steps, {base['open_count']} open, "
        f"{base['done_count']} done)."
    )
    return base


def mark_step(repo_root: Path, index: int, *, done: bool = True) -> Path:
    """Mark 1-based step index done/undone and rewrite file."""
    path = bite_plan_path(repo_root)
    if not path.is_file():
        raise FileNotFoundError(f"No bite plan at {path}")
    text = path.read_text(encoding="utf-8")
    steps = parse_steps(text)
    if index < 1 or index > len(steps):
        raise IndexError(f"Step {index} out of range 1..{len(steps)}")
    steps[index - 1]["done"] = bool(done)

    # Prefer keep existing goal/header if present
    goal = "Work"
    architecture = ""
    tech_stack = ""
    for line in text.splitlines():
        if line.startswith("**Goal:**"):
            goal = line.split(":**", 1)[-1].strip() or goal
        elif line.startswith("**Architecture:**"):
            architecture = line.split(":**", 1)[-1].strip()
        elif line.startswith("**Tech stack:**"):
            tech_stack = line.split(":**", 1)[-1].strip()
        elif line.startswith("# Bite plan:"):
            goal = line.split(":", 1)[-1].strip() or goal

    write_bite_plan(
        repo_root,
        goal=goal,
        steps=steps,
        architecture=architecture,
        tech_stack=tech_stack,
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC bite plan: 2–5 min checkbox steps → BITE_PLAN.md"
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="Print JSON assessment")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write BITE_PLAN.md from --goal / --step",
    )
    parser.add_argument("--goal", default="", help="Plan goal (with --write)")
    parser.add_argument(
        "--step",
        action="append",
        default=[],
        dest="steps",
        help="Bite step (repeatable; with --write)",
    )
    parser.add_argument("--architecture", default="", help="Optional architecture line")
    parser.add_argument("--tech-stack", default="", help="Optional tech stack line")
    parser.add_argument(
        "--mark",
        type=int,
        default=0,
        help="1-based step index to mark done/undone",
    )
    parser.add_argument(
        "--undone",
        action="store_true",
        help="With --mark: set step open instead of done",
    )
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.write:
        goal = (args.goal or "").strip() or "Work"
        steps = args.steps or []
        write_bite_plan(
            repo,
            goal=goal,
            steps=steps,
            architecture=args.architecture,
            tech_stack=args.tech_stack,
        )

    if args.mark:
        try:
            mark_step(repo, args.mark, done=not args.undone)
        except (FileNotFoundError, IndexError) as exc:
            if args.json:
                print(json.dumps({"status": "error", "message": str(exc)}))
            else:
                print(str(exc), file=sys.stderr)
            return 1

    result = assess_bite_plan(repo)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"status={result['status']} steps={result['step_count']} open={result['open_count']}")
        print(result["message"])
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
