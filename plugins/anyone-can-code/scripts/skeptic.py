#!/usr/bin/env python3
"""Pure helpers for $skeptic — list review scope via git (mockable).

Does not review code. Does not write the tree. Optional save path is skill-only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence


RunCommand = Callable[[list[str], Path], subprocess.CompletedProcess[str]]


def default_run_command(
    command: list[str], cwd: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def _parse_porcelain(stdout: str) -> list[str]:
    files: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        # XY<path> or XY <path> / rename lines — take last path token after status
        body = line[3:] if len(line) >= 3 else line
        body = body.strip()
        if " -> " in body:
            body = body.split(" -> ", 1)[1].strip()
        if body:
            files.append(body)
    return files


def list_changed_files(
    cwd: Path | str = ".",
    *,
    named_paths: Sequence[str] | None = None,
    base: str | None = None,
    run_command: RunCommand | None = None,
) -> list[str]:
    """Return paths to review.

    Named paths win (no git). Else working tree via `git status --porcelain`,
    or `git diff --name-only <base>` when base is set.
    """
    if named_paths is not None:
        return [p.strip() for p in named_paths if p and str(p).strip()]

    run = run_command or default_run_command
    root = Path(cwd)
    if base:
        result = run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", base],
            root,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    result = run(["git", "status", "--porcelain", "-u"], root)
    if result.returncode != 0:
        return []
    return _parse_porcelain(result.stdout)


def format_skeptic_md(
    *,
    scope: Sequence[str],
    findings: Sequence[dict],
    summary: str,
) -> str:
    """Render a plain SKEPTIC.md body (skill writes only if user asks)."""
    lines = [
        "# Skeptic review",
        "",
        "Read-only second pass. This does not replace $verify (ship gate still verify).",
        "",
        "## Scope",
    ]
    if scope:
        lines.extend(f"- `{path}`" for path in scope)
    else:
        lines.append("- (none)")
    lines += ["", "## Findings"]
    if not findings:
        lines.append("- none")
    else:
        for item in findings:
            sev = item.get("severity", "info")
            view = item.get("view", "general")
            file_ref = item.get("file", "")
            note = item.get("note", "")
            loc = f" `{file_ref}`" if file_ref else ""
            lines.append(f"- **{sev}** / {view}{loc}: {note}")
    lines += ["", "## Summary", str(summary or "").strip() or "(empty)", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ACC skeptic scope helper")
    parser.add_argument(
        "--list-changed",
        action="store_true",
        help="Print changed files (one per line) or JSON with --json",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Git base ref for diff --name-only (e.g. main)",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Repo path (default: .)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON list",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Named paths override git when provided after --",
    )
    args = parser.parse_args(argv)

    if not args.list_changed:
        parser.print_help()
        return 2

    named = args.paths if args.paths else None
    files = list_changed_files(
        args.cwd,
        named_paths=named,
        base=args.base,
    )
    if args.json:
        print(json.dumps(files))
    else:
        for path in files:
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
