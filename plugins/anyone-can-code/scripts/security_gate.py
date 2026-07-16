#!/usr/bin/env python3
"""Production security gate — CHEAP local scan before any deploy.

Biggest audit miss (beta.3): first production ship had open signup + admin123.
This gate is a hard checklist. User decides whether to ship; gate only reports.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# Patterns that mean "not safe for real users yet"
CHECKS: list[dict[str, Any]] = [
    {
        "id": "open_signup",
        "title": "Open public signup",
        "plain": "Anyone can create an account without invite. Turn public signup OFF for first launch.",
        "regexes": [
            re.compile(r"ALLOW_PUBLIC_REGISTRATION\s*[=:]\s*[\"']?true", re.I),
            re.compile(r"public[_-]?registration\s*[=:]\s*[\"']?true", re.I),
            re.compile(r"OPEN_SIGNUP\s*[=:]\s*[\"']?true", re.I),
            re.compile(r"enable[d]?_public_signup\s*[=:]\s*true", re.I),
        ],
    },
    {
        "id": "default_password",
        "title": "Default password",
        "plain": "A default password is hard-coded (example: admin123). Set a real secret first.",
        "regexes": [
            re.compile(r"DEFAULT_ADMIN_PASSWORD\s*[=:]\s*[\"'][^\"']+[\"']", re.I),
            re.compile(r"admin[_-]?password\s*[=:]\s*[\"']admin123[\"']", re.I),
            re.compile(r"[\"']admin123[\"']"),
            re.compile(r"password\s*=\s*[\"']password[\"']", re.I),
            re.compile(r"password\s*=\s*[\"']changeme[\"']", re.I),
        ],
    },
    {
        "id": "missing_db_policy",
        "title": "Database who-can-see-what off",
        "plain": "Database rules that keep each user's data separate look turned off or missing.",
        "regexes": [
            re.compile(r"ENABLE_RLS\s*[=:]\s*[\"']?false", re.I),
            re.compile(r"row[_ ]?level[_ ]?security\s*[=:]\s*[\"']?false", re.I),
            re.compile(r"DISABLE_RLS\s*[=:]\s*[\"']?true", re.I),
        ],
    },
    {
        "id": "placeholder_secret",
        "title": "Placeholder secret",
        "plain": "A secret still looks like a placeholder (changeme / your-secret / TODO). Set real secrets.",
        "regexes": [
            re.compile(r"(SECRET|API_KEY|TOKEN)\s*[=:]\s*[\"']?(changeme|your[_-]?secret|todo|xxx)[\"']?", re.I),
            re.compile(r"sk-your[_-]?api[_-]?key", re.I),
        ],
    },
]

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
    ".codex",
}
TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".env",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".sql",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".java",
    ".cs",
}


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            ".env",
            ".env.local",
            ".env.production",
            "Dockerfile",
        }:
            # allow common env files without suffix match already covered
            if not path.name.startswith(".env"):
                continue
        files.append(path)
    return files


def scan_project(root: Path, *, max_file_bytes: int = 400_000) -> dict[str, Any]:
    """Scan project files. Returns pass/fail checklist in plain words."""
    root = Path(root)
    findings: list[dict[str, Any]] = []
    files_scanned = 0
    for path in _iter_files(root):
        try:
            if path.stat().st_size > max_file_bytes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files_scanned += 1
        for check in CHECKS:
            for rx in check["regexes"]:
                m = rx.search(text)
                if not m:
                    continue
                rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
                findings.append(
                    {
                        "id": check["id"],
                        "title": check["title"],
                        "plain": check["plain"],
                        "file": rel,
                        "snippet": m.group(0)[:120],
                    }
                )
                break  # one hit per check per file
    # de-dupe by id+file
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for f in findings:
        key = (f["id"], f["file"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    failed_ids = sorted({f["id"] for f in unique})
    summary_lines = []
    # Fail closed on empty scan: 0 files is not "safe" — wrong cwd/root or empty tree.
    if files_scanned == 0:
        ok = False
        summary_lines.append(
            "Security gate: FAIL. Scanned 0 files (wrong project root, empty tree, "
            "or nothing readable). Not a PASS — fix the path, then re-scan."
        )
    elif unique:
        ok = False
        summary_lines.append(
            f"Security gate: FAIL ({len(unique)} hit(s)). Do not ship until fixed or user explicitly accepts risk."
        )
        for f in unique[:12]:
            summary_lines.append(f"- {f['title']} in {f['file']}: {f['plain']}")
    else:
        ok = True
        summary_lines.append(
            "Security gate: PASS. No open-signup / default-password / placeholder-secret hits."
        )

    return {
        "ok": ok,
        "files_scanned": files_scanned,
        "findings": unique,
        "failed_ids": failed_ids,
        "summary_lines": summary_lines,
        "user_line": summary_lines[0],
        "checklist": [
            "No open public signup for first launch",
            "No default passwords (no admin123)",
            "Database who-can-see-what rules on",
            "Real secrets set (not changeme)",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ACC production security gate")
    parser.add_argument("path", nargs="?", default=".", help="Project root to scan")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args(argv)
    result = scan_project(Path(args.path).resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for line in result["summary_lines"]:
            print(line)
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
