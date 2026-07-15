#!/usr/bin/env python3
"""Model performance ledger — records outcomes per task type and recommends best model."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

# Codex-first defaults (not always max reasoning — audit: HIGH everywhere burned limit)
DEFAULT_MODEL = "gpt-5.6"
DEFAULT_REASONING = "medium"
DEFAULT_LEDGER_PATH = Path(".codex/anyone-can-code/state/model-ledger.jsonl")

# Task scale → starting reasoning (prefer cheaper when possible)
REASONING_BY_TASK = {
    "micro": "low",
    "bug": "medium",
    "bug-fix": "medium",
    "feature": "medium",
    "research": "high",
    "product": "high",
    "general": "medium",
}


def _resolve_path(ledger_path: Path | None) -> Path:
    return Path(ledger_path) if ledger_path is not None else DEFAULT_LEDGER_PATH


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
    record = {
        "model": model,
        "task_type": task_type,
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
    key = (task_type or "general").strip().lower()
    return REASONING_BY_TASK.get(key, DEFAULT_REASONING)


def recommend_model(
    task_type: str,
    *,
    ledger_path: Path | None = None,
) -> dict[str, str]:
    path = _resolve_path(ledger_path)
    records = [r for r in _load_records(path) if r.get("task_type") == task_type]
    reasoning = recommend_reasoning(task_type)

    if not records:
        return {
            "model": DEFAULT_MODEL,
            "reasoning": reasoning,
            "reason": f"no data for {task_type!r} — default used; reasoning={reasoning}",
        }

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
        return {
            "model": DEFAULT_MODEL,
            "reasoning": reasoning,
            "reason": f"no usable records — default used; reasoning={reasoning}",
        }

    best = max(scores, key=lambda m: scores[m])
    return {
        "model": best,
        "reasoning": reasoning,
        "reason": (
            f"best score {scores[best]} for {task_type!r} across {len(records)} records; "
            f"reasoning={reasoning} (not always high)"
        ),
    }


def extract_model_from_payload(payload: dict[str, Any]) -> str:
    return str(payload.get("model") or DEFAULT_MODEL)


def extract_reasoning_from_payload(payload: dict[str, Any]) -> str:
    raw = payload.get("model_reasoning_effort") or payload.get("reasoning") or ""
    return str(raw).strip().lower() or DEFAULT_REASONING
