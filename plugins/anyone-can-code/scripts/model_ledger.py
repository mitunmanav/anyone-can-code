#!/usr/bin/env python3
"""Model performance ledger — records outcomes per task type and recommends best model."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

# Codex-first defaults (not always max reasoning — audit: HIGH everywhere burned limit)
DEFAULT_MODEL = "gpt-5.6"
DEFAULT_REASONING = "medium"
DEFAULT_LEDGER_PATH = Path(".codex/anyone-can-code/state/model-ledger.jsonl")
DEFAULT_TASK_TYPE = "general"

# Canonical ledger task types (write + recommend must use the same set)
KNOWN_TASK_TYPES = frozenset(
    {
        "micro",
        "bug",
        "bug-fix",
        "feature",
        "research",
        "product",
        "plan",
        "verify",
        "general",
    }
)

# Route / entry-mode aliases → ledger task_type
ROUTE_ALIASES = {
    "bug-fix": "bug-fix",
    "bugfix": "bug-fix",
    "bug": "bug-fix",
    "debug": "bug-fix",
    "fix": "bug-fix",
    "feature": "feature",
    "feature-request": "feature",
    "implement": "feature",
    "build": "feature",
    "micro": "micro",
    "nit": "micro",
    "research": "research",
    "explore": "research",
    "product": "product",
    "idea": "product",
    "plan": "plan",
    "written-spec": "plan",
    "verify": "verify",
    "ship-verify": "verify",
    "polish-review": "verify",
    "general": "general",
}

# Soft cost classes for efficiency tips only (labels, not host APIs).
# GPT-5.6 family spirit: Sol=full · Terra=mid · Luna=cheap — suggest only.
_CHEAP_MARKERS = (
    "luna",
    "mini",
    "haiku",
    "flash",
    "nano",
    "small",
    "lite",
    "cheap",
)
_HUNGRY_MARKERS = (
    "sol",
    "opus",
    "o1",
    "o3",
    "max",
    "pro",
    "ultra",
)


def model_cost_class(model: str) -> str:
    """Label-only cost class for soft tips. Never controls host picker."""
    m = (model or "").strip().lower()
    if not m:
        return "mid"
    if any(token in m for token in _CHEAP_MARKERS):
        return "cheap"
    if any(token in m for token in _HUNGRY_MARKERS):
        return "hungry"
    return "mid"


def soft_efficiency_tip(recommended: str) -> str:
    """Honest soft tip — ACC suggests cheaper labels; host picker is out of scope."""
    rec = (recommended or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return (
        f"Efficiency soft tip: prefer lower-cost model if host allows "
        f"(Luna/mini class; Sol/Terra/Luna = full/mid/cheap labels). "
        f"Ledger suggestion: {rec}. "
        "ACC never forces host model picker APIs."
    )


# Task scale → starting reasoning (prefer cheaper when possible)
REASONING_BY_TASK = {
    "micro": "low",
    "bug": "medium",
    "bug-fix": "medium",
    "feature": "medium",
    "research": "high",
    "product": "high",
    "plan": "medium",
    "verify": "medium",
    "general": "medium",
}

# Ordered rules: first match wins. (task_type, keyword tokens in lower text)
_KEYWORD_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "bug-fix",
        (
            "bug",
            "bugfix",
            "bug-fix",
            "fix the",
            "fix a",
            "null pointer",
            "stack trace",
            "regression",
            "crash",
            "exception",
            "traceback",
            "failing test",
            "broken",
            "debug",
            "error handling",
        ),
    ),
    (
        "micro",
        (
            "typo",
            "rename",
            "one line",
            "one-liner",
            "nit",
            "tiny change",
            "tiny fix",
            "quick fix",
            "whitespace",
            "format only",
        ),
    ),
    (
        "research",
        (
            "research",
            "investigate",
            "explore",
            "how does",
            "what is",
            "lookup",
            "look up",
            "read the docs",
            "documentation",
            "survey",
        ),
    ),
    (
        "product",
        (
            "product",
            "roadmap",
            "pricing",
            "user story",
            "persona",
            "go to market",
            "onboard",
            "first run",
        ),
    ),
    (
        "plan",
        (
            "write a plan",
            "make a plan",
            "planning",
            "spec",
            "design doc",
            "architecture",
            "checklist",
            "breakdown",
        ),
    ),
    (
        "verify",
        (
            "verify",
            "pytest",
            "unit test",
            "test suite",
            "doctor",
            "smoke test",
            "regression test",
            "proof",
            "ci green",
        ),
    ),
    (
        "feature",
        (
            "feature",
            "implement",
            "add support",
            "build out",
            "new endpoint",
            "new page",
            "ship",
            "wire up",
        ),
    ),
)

# skill name / id → task_type (substring match on lower skill)
_SKILL_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bug-fix", ("fix", "debug", "systematic-debugging")),
    ("plan", ("plan", "writing-plans", "clarify", "brainstorm")),
    ("verify", ("verify", "verification-before-completion", "tdd", "test-driven")),
    ("feature", ("execute", "implement", "build", "subagent-driven")),
    ("research", ("learn", "wiki", "research", "docs")),
    ("product", ("product", "onboard", "setup", "orchestrator")),
    ("micro", ("readable", "polish")),
)

# tool names → task_type (exact-ish / substring on lower tool name)
_TOOL_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("research", ("websearch", "web_search", "webfetch", "web_fetch", "browser")),
    ("bug-fix", ("debugger", "stacktrace")),
    ("verify", ("pytest",)),
    ("feature", ("apply_patch", "edit", "write")),
)


def _resolve_path(ledger_path: Path | None) -> Path:
    return Path(ledger_path) if ledger_path is not None else DEFAULT_LEDGER_PATH


def _norm_token(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_task_type(raw: str | None) -> str | None:
    """Map free text / route token to a known task_type, or None if unknown."""
    key = _norm_token(raw).replace("_", "-")
    if not key:
        return None
    if key in KNOWN_TASK_TYPES:
        return key
    if key in ROUTE_ALIASES:
        return ROUTE_ALIASES[key]
    # allow "bug fix" style
    compact = key.replace(" ", "-")
    if compact in KNOWN_TASK_TYPES:
        return compact
    if compact in ROUTE_ALIASES:
        return ROUTE_ALIASES[compact]
    return None


def _iter_lower(items: Iterable[str] | None) -> list[str]:
    if not items:
        return []
    return [_norm_token(str(x)) for x in items if str(x).strip()]


def classify_task_type(
    *,
    text: str = "",
    tools: Iterable[str] | None = None,
    skills: Iterable[str] | None = None,
    route: str | None = None,
    signals: list[dict[str, Any]] | None = None,
) -> str:
    """Deterministic task_type from route, skills, tools, keywords, signals.

    Never invent host APIs. Same labels for ledger write and recommend filters.
    Priority: explicit route → skills → tools → keyword text → signal detail → general.
    """
    # 1) explicit route / entry mode if already a known type
    routed = normalize_task_type(route)
    if routed and routed != DEFAULT_TASK_TYPE:
        return routed

    # Pull tool/skill/detail crumbs from signals when callers pass them
    tool_list = _iter_lower(tools)
    skill_list = _iter_lower(skills)
    text_blob = _norm_token(text)
    if signals:
        for row in signals:
            if not isinstance(row, dict):
                continue
            for key in ("tool_name", "tool", "toolName"):
                val = row.get(key)
                if val:
                    tool_list.append(_norm_token(str(val)))
            for key in ("skill", "skill_name", "skillName"):
                val = row.get(key)
                if val:
                    skill_list.append(_norm_token(str(val)))
            detail = row.get("detail") or row.get("signal_type") or ""
            if detail:
                text_blob = f"{text_blob} {_norm_token(str(detail))}".strip()

    # 2) skills (strong intent signal)
    for task_type, markers in _SKILL_RULES:
        for skill in skill_list:
            if any(m in skill for m in markers):
                return task_type

    # 3) tools
    for task_type, markers in _TOOL_RULES:
        for tool in tool_list:
            if any(m in tool for m in markers):
                return task_type

    # 4) user / summary keywords
    if text_blob:
        for task_type, markers in _KEYWORD_RULES:
            if any(m in text_blob for m in markers):
                return task_type

    # 5) bare route that only normalized to general, or nothing
    if routed:
        return routed
    return DEFAULT_TASK_TYPE


def record_model_result(
    model: str,
    task_type: str,
    outcome: str,
    *,
    reasoning: str | None = None,
    ledger_path: Path | None = None,
) -> None:
    path = _resolve_path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_task_type(task_type) or _norm_token(task_type) or DEFAULT_TASK_TYPE
    if normalized not in KNOWN_TASK_TYPES:
        # keep unknown labels but prefer known set
        normalized = normalized or DEFAULT_TASK_TYPE
    record = {
        "model": model,
        "task_type": normalized,
        "outcome": outcome,
        "reasoning": (reasoning or "").strip().lower() or None,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def recommend_reasoning(task_type: str) -> str:
    """Never default to max effort. Prefer medium/low."""
    key = normalize_task_type(task_type) or _norm_token(task_type) or DEFAULT_TASK_TYPE
    return REASONING_BY_TASK.get(key, DEFAULT_REASONING)


def recommend_model(
    task_type: str,
    *,
    ledger_path: Path | None = None,
    efficiency: bool = False,
) -> dict[str, Any]:
    path = _resolve_path(ledger_path)
    want = normalize_task_type(task_type) or _norm_token(task_type) or DEFAULT_TASK_TYPE
    records = [
        r
        for r in _load_records(path)
        if (normalize_task_type(str(r.get("task_type") or "")) or r.get("task_type")) == want
    ]
    reasoning = recommend_reasoning(want)

    def _soft(out: dict[str, Any], model: str) -> dict[str, Any]:
        if efficiency:
            out["soft"] = True
            out["tip"] = soft_efficiency_tip(model)
            out["reason"] = str(out.get("reason") or "") + " [soft tip only; host picker not controlled]"
        return out

    if not records:
        return _soft(
            {
                "model": DEFAULT_MODEL,
                "reasoning": reasoning,
                "reason": f"no data for {want!r} — default used; reasoning={reasoning}",
            },
            DEFAULT_MODEL,
        )

    scores: dict[str, int] = defaultdict(int)
    for r in records:
        model = r.get("model", "")
        if not model:
            continue
        if r.get("outcome") == "success":
            scores[model] += 1
        else:
            scores[model] -= 1

    if not scores:
        return _soft(
            {
                "model": DEFAULT_MODEL,
                "reasoning": reasoning,
                "reason": f"no usable records — default used; reasoning={reasoning}",
            },
            DEFAULT_MODEL,
        )

    best = max(scores, key=lambda m: scores[m])
    reason = (
        f"best score {scores[best]} for {want!r} across {len(records)} records; "
        f"reasoning={reasoning} (not always high)"
    )
    if efficiency:
        best_score = scores[best]
        cheap_ok = [
            m
            for m, sc in scores.items()
            if sc > 0
            and model_cost_class(m) == "cheap"
            and sc >= best_score - 1
        ]
        if cheap_ok:
            preferred = max(cheap_ok, key=lambda m: (scores[m], -len(m)))
            if preferred != best:
                reason = (
                    f"efficiency soft-prefer {preferred!r} (score {scores[preferred]}) "
                    f"over {best!r} (score {best_score}) for {want!r}; "
                    f"reasoning={reasoning} (not always high)"
                )
                best = preferred
            else:
                reason = (
                    f"best score {scores[best]} for {want!r} across {len(records)} "
                    f"records (cheap label); reasoning={reasoning} (not always high)"
                )
    return _soft(
        {
            "model": best,
            "reasoning": reasoning,
            "reason": reason,
        },
        best,
    )


def extract_model_from_payload(payload: dict[str, Any]) -> str:
    # Codex hooks common input: model is a Codex-specific extension (slug).
    return str(payload.get("model") or DEFAULT_MODEL)


def extract_reasoning_from_payload(payload: dict[str, Any]) -> str:
    raw = payload.get("model_reasoning_effort") or payload.get("reasoning") or ""
    return str(raw).strip().lower() or DEFAULT_REASONING


def task_type_from_session(
    *,
    payload: dict[str, Any] | None = None,
    workflow: dict[str, Any] | None = None,
    signals: list[dict[str, Any]] | None = None,
) -> str:
    """Product helper: classify from Stop/SessionStart context already on disk."""
    payload = payload or {}
    workflow = workflow or {}
    text = " ".join(
        [
            str(payload.get("last_assistant_message") or ""),
            str(payload.get("prompt") or ""),
            str(workflow.get("last_task") or ""),
            str(workflow.get("active_task") or ""),
            str(workflow.get("active_goal") or ""),
            str(workflow.get("next_step") or ""),
            str(workflow.get("route") or ""),
        ]
    )
    tools: list[str] = []
    skills: list[str] = []
    for key in ("tool_name", "tools", "tool_names"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            tools.append(val)
        elif isinstance(val, (list, tuple)):
            tools.extend(str(x) for x in val)
    for key in ("skill", "skills", "skill_name"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            skills.append(val)
        elif isinstance(val, (list, tuple)):
            skills.extend(str(x) for x in val)
    return classify_task_type(
        text=text,
        tools=tools,
        skills=skills,
        route=str(workflow.get("route") or payload.get("route") or "") or None,
        signals=signals,
    )
