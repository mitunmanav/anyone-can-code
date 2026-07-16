#!/usr/bin/env python3
"""Detect silent failures — exit 0 but something is wrong."""

from __future__ import annotations

import re
from typing import Any

SILENT_INDICATORS = [
    ("empty output with exit 0", lambda o, e: e == 0 and not o.strip()),
    ("null result with exit 0", lambda o, e: e == 0 and o.strip() in {"null", "None", "undefined", "{}"}),
]

WARNING_PATTERNS = [
    r"\bwarning\b",
    r"\bwarn\b",
    r"\bskipped?\b",
    r"\bdeprecated?\b",
    r"\btimeout\b",
    r"\bretrying\b",
    r"\bfallback\b",
    r"\bignored?\b",
]


def scan_tool_response(response: dict[str, Any]) -> dict[str, list[str]]:
    output = str(response.get("output") or response.get("stdout") or "")
    exit_code = int(response.get("exit_code", response.get("returncode", 0)) or 0)

    if exit_code != 0:
        return {"silent_failures": []}

    silent_failures: list[str] = []

    for label, check in SILENT_INDICATORS:
        if check(output, exit_code):
            silent_failures.append(label)

    if not silent_failures:
        for pattern in WARNING_PATTERNS:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                silent_failures.append(f"warning or skip detected: '{match.group()}'")
                break

    return {"silent_failures": silent_failures}
