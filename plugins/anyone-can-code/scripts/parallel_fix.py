#!/usr/bin/env python3
"""Parse pytest failure output → unique failed test file paths.

Pure helper for $parallel-fix skill. No network. No test runner.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# FAILED|ERROR nodeid lines from short summary / progress.
# Examples:
#   FAILED tests/test_b.py::test_two - AssertionError
#   ERROR tests/test_c.py::test_three - RuntimeError
#   FAILED C:\repo\tests\test_win.py::test_x - assert False
_FAIL_LINE = re.compile(
    r"^(?:FAILED|ERROR)\s+(\S+?)(?:::|\s|$)",
    re.MULTILINE | re.IGNORECASE,
)

# Progress form: path::node FAILED / ERROR (optional trailing message)
_PROGRESS_FAIL = re.compile(
    r"^(\S+?\.py)::\S+\s+(?:FAILED|ERROR)\b",
    re.MULTILINE | re.IGNORECASE,
)


def _normalize_path(raw: str) -> str | None:
    """Keep only paths that look like Python files; strip drive noise lightly."""
    text = raw.strip().strip("\"'")
    if not text:
        return None
    # Drop trailing punctuation from summary glue
    text = text.rstrip(".,;:")
    if ".py" not in text.lower():
        return None
    # Windows path → forward slashes for stable keys
    text = text.replace("\\", "/")
    # If absolute, keep relative-looking tail when possible
    lower = text.lower()
    for marker in ("/tests/", "/test/"):
        idx = lower.rfind(marker)
        if idx >= 0:
            # keep from tests/ (or test/) onward when path has a clear segment
            return text[idx + 1 :] if text[idx] == "/" else text[idx:]
    # Already relative or unknown layout
    if text.startswith("/") or re.match(r"^[A-Za-z]:/", text):
        return Path(text).name if "/" not in text.rstrip("/") else text.lstrip("/")
    return text


def parse_failed_files(output: str) -> list[str]:
    """Return unique failed/errored test files in first-seen order."""
    if not output:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for pattern in (_FAIL_LINE, _PROGRESS_FAIL):
        for match in pattern.finditer(output):
            path = _normalize_path(match.group(1))
            if not path or path in seen:
                continue
            # Must end with .py after normalize
            if not path.lower().endswith(".py"):
                continue
            seen.add(path)
            ordered.append(path)
    return ordered


def main(argv: list[str] | None = None, stdin_text: str | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse pytest output → failed test file paths (one per line)."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="-",
        help="Path to pytest log, or '-' for stdin (default)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON array instead of one path per line",
    )
    args = parser.parse_args(argv)

    if args.source == "-":
        text = stdin_text if stdin_text is not None else sys.stdin.read()
    else:
        text = Path(args.source).read_text(encoding="utf-8", errors="replace")

    files = parse_failed_files(text)
    if args.json:
        print(json.dumps(files))
    else:
        for path in files:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
