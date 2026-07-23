"""Load blind scenarios (JSON) and block coaching prompts."""
from __future__ import annotations

import json
import re
from pathlib import Path

COACHING_PATTERNS = [
    re.compile(r"\$[a-z_]+", re.I),
    re.compile(r"\buse ACC\b", re.I),
    re.compile(r"\bAnyone Can Code\b.*\$(setup|verify|plan)", re.I),
    re.compile(r"\bPHASE\d+_OK\b"),
    re.compile(r"\b(SETUP|VERIFY|FIX)_OK\b"),
]


def load_pack(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"scenario pack must be object: {path}")
    return data


def load_scenarios(path: Path) -> list[dict]:
    data = load_pack(path)
    items = data.get("scenarios") or []
    if not items:
        raise ValueError(f"no scenarios in {path}")
    return items


def assert_no_coaching(items: list[dict]) -> None:
    for it in items:
        blobs = [it.get("prompt") or ""]
        blobs.extend(it.get("retries") or [])
        for b in blobs:
            for pat in COACHING_PATTERNS:
                if pat.search(b):
                    raise AssertionError(
                        f"coaching pattern {pat.pattern!r} in scenario "
                        f"{it.get('id')}: {b[:120]!r}"
                    )
