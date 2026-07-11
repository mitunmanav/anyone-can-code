#!/usr/bin/env python3
"""Model performance ledger — records outcomes per task type and recommends best model."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_LEDGER_PATH = Path(".codex/anyone-can-code/state/model-ledger.jsonl")


def _resolve_path(ledger_path: Path | None) -> Path:
    return Path(ledger_path) if ledger_path is not None else DEFAULT_LEDGER_PATH


def record_model_result(
    model: str,
    task_type: str,
    outcome: str,
    *,
    ledger_path: Path | None = None,
) -> None:
    path = _resolve_path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"model": model, "task_type": task_type, "outcome": outcome}
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


def recommend_model(
    task_type: str,
    *,
    ledger_path: Path | None = None,
) -> dict[str, str]:
    path = _resolve_path(ledger_path)
    records = [r for r in _load_records(path) if r.get("task_type") == task_type]

    if not records:
        return {"model": DEFAULT_MODEL, "reason": f"no data for {task_type!r} — default used"}

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
        return {"model": DEFAULT_MODEL, "reason": "no usable records — default used"}

    best = max(scores, key=lambda m: scores[m])
    return {"model": best, "reason": f"best score {scores[best]} for {task_type!r} across {len(records)} records"}


def extract_model_from_payload(payload: dict[str, Any]) -> str:
    return str(payload.get("model") or DEFAULT_MODEL)
