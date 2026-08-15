#!/usr/bin/env python3
"""Detect project lint/test tools (pytest / ruff / eslint).

Aider-style after-edit check helper for $auto-lint and optional soft
PostToolUse hint (pref auto_lint=true). Detect + format only — never
fail-closed; never writes project files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EDIT_TOOL_MARKERS = (
    "apply_patch",
    "applypatch",
    "edit",
    "write",
    "multiedit",
    "create_file",
    "str_replace",
    "search_replace",
)


def _pyproject_text(root: Path) -> str:
    path = root / "pyproject.toml"
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _package_json(root: Path) -> dict[str, Any]:
    path = root / "package.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _has_eslint_config(root: Path) -> bool:
    names = (
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
        "eslint.config.ts",
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.json",
        ".eslintrc.yml",
        ".eslintrc.yaml",
    )
    if any((root / name).exists() for name in names):
        return True
    return False


def _deps_mention_eslint(pkg: dict[str, Any]) -> bool:
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        block = pkg.get(key) or {}
        if isinstance(block, dict) and "eslint" in block:
            return True
    scripts = pkg.get("scripts") or {}
    if isinstance(scripts, dict):
        for value in scripts.values():
            if isinstance(value, str) and re.search(r"\beslint\b", value):
                return True
    return False


def detect_tools(project_root: Path) -> list[dict[str, str]]:
    """Return detected tools with name, kind, command, evidence (stable order)."""
    root = Path(project_root)
    tools: list[dict[str, str]] = []
    pyproject = _pyproject_text(root)

    # ruff (lint) first — cheap check before tests
    if (
        (root / "ruff.toml").is_file()
        or (root / ".ruff.toml").is_file()
        or "[tool.ruff" in pyproject
    ):
        tools.append(
            {
                "name": "ruff",
                "kind": "lint",
                "command": "ruff check .",
                "evidence": "ruff config present",
            }
        )

    # pytest
    if (
        (root / "tests").is_dir()
        or (root / "test").is_dir()
        or (root / "pytest.ini").is_file()
        or (root / "conftest.py").is_file()
        or "[tool.pytest" in pyproject
        or re.search(r"(?m)^\s*[\"']?pytest[\"']?\s*[=\[]", pyproject)
    ):
        tools.append(
            {
                "name": "pytest",
                "kind": "test",
                "command": "python -m pytest -q",
                "evidence": "pytest layout or config present",
            }
        )

    # eslint
    pkg = _package_json(root)
    if _has_eslint_config(root) or _deps_mention_eslint(pkg):
        tools.append(
            {
                "name": "eslint",
                "kind": "lint",
                "command": "npx eslint .",
                "evidence": "eslint config or dependency present",
            }
        )

    return tools


def format_post_edit_hint(tools: list[dict[str, str]]) -> str:
    """Soft agent context after an edit. Empty when nothing to run."""
    if not tools:
        return ""
    cmds = "; ".join(t["command"] for t in tools)
    names = ", ".join(t["name"] for t in tools)
    return (
        f"AUTO-LINT (pref on): detected {names}. After this edit, run: {cmds}. "
        "Or use $auto-lint. Fix failures before claiming done. Soft hint only — not a block."
    )


def is_edit_like_tool(tool_name: str) -> bool:
    name = str(tool_name or "").strip().lower().replace("-", "").replace("_", "")
    if not name:
        return False
    return any(marker in name for marker in EDIT_TOOL_MARKERS)


def pref_enabled(prefs: dict[str, Any] | None) -> bool:
    """Opt-in only. Default off when missing."""
    if not prefs:
        return False
    val = prefs.get("auto_lint", False)
    if val is True:
        return True
    if isinstance(val, (int, float)) and val == 1:
        return True
    if isinstance(val, str) and val.strip().lower() in {"true", "1", "yes", "on"}:
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect pytest/ruff/eslint in a project (no write, no fail-closed)."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON list of tools",
    )
    parser.add_argument(
        "--hint",
        action="store_true",
        help="Emit soft post-edit hint text (empty if none)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    tools = detect_tools(root)
    if args.hint:
        print(format_post_edit_hint(tools), end="" if not tools else "\n")
        return 0
    if args.json:
        print(json.dumps(tools, indent=2 if sys.stdout.isatty() else None))
    else:
        if not tools:
            print("none")
        else:
            for tool in tools:
                print(f"{tool['name']}\t{tool['kind']}\t{tool['command']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
