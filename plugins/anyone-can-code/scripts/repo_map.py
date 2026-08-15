#!/usr/bin/env python3
"""Ranked repo map — Aider-inspired, pure Python, no AI.

Scans source files, extracts top-level symbols via regex, ranks by
cross-file name reference frequency (cheap graph ranking), writes a
capped sample to `.codex/anyone-can-code/artifacts/repo-map.md`.

SessionStart may inject a thin slice **only if that file already exists**.
Stdlib only. No network. No LLM.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REL_PATH = Path(".codex/anyone-can-code/artifacts/repo-map.md")
INJECT_MAX_CHARS = 600
DEFAULT_MAX_FILES = 40
DEFAULT_MAX_SYMBOLS = 8
DEFAULT_MAP_MAX_CHARS = 12_000
DEFAULT_MAX_SCAN_FILES = 800
DEFAULT_MAX_FILE_BYTES = 200_000

IGNORE_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".codex",
        ".claude",
        ".grok",
        ".codegraph",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".tox",
        ".eggs",
        "dist",
        "build",
        "coverage",
        "htmlcov",
        "target",
        "vendor",
        ".next",
        ".nuxt",
        ".turbo",
        "Pods",
        "DerivedData",
    }
)

SOURCE_EXTS = frozenset(
    {
        ".py",
        ".pyi",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".go",
        ".rs",
        ".java",
        ".kt",
        ".kts",
        ".rb",
        ".php",
        ".cs",
        ".swift",
        ".c",
        ".h",
        ".cpp",
        ".cc",
        ".hpp",
        ".m",
        ".mm",
        ".scala",
        ".vue",
        ".svelte",
    }
)

# Top-level-ish definition patterns (language-light; not a full parser).
_SYMBOL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?m)^class\s+([A-Za-z_][\w]*)\b"), "class"),
    (re.compile(r"(?m)^(?:async\s+)?def\s+([A-Za-z_][\w]*)\b"), "def"),
    (re.compile(r"(?m)^export\s+(?:async\s+)?function\s+([A-Za-z_][\w]*)\b"), "function"),
    (re.compile(r"(?m)^export\s+class\s+([A-Za-z_][\w]*)\b"), "class"),
    (re.compile(r"(?m)^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][\w]*)\b"), "function"),
    (re.compile(r"(?m)^(?:export\s+)?class\s+([A-Za-z_][\w]*)\b"), "class"),
    (re.compile(r"(?m)^func\s+(?:\([^)]*\)\s*)?([A-Z][\w]*)\b"), "func"),
    (re.compile(r"(?m)^type\s+([A-Z][\w]*)\b"), "type"),
    (re.compile(r"(?m)^(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_][\w]*)\b"), "fn"),
    (re.compile(r"(?m)^(?:pub\s+)?struct\s+([A-Za-z_][\w]*)\b"), "struct"),
    (re.compile(r"(?m)^(?:pub\s+)?enum\s+([A-Za-z_][\w]*)\b"), "enum"),
    (re.compile(r"(?m)^(?:public\s+|private\s+|protected\s+)?(?:static\s+)?class\s+([A-Za-z_][\w]*)\b"), "class"),
    (re.compile(r"(?m)^(?:public\s+|private\s+|protected\s+)?interface\s+([A-Za-z_][\w]*)\b"), "interface"),
]

# Identifiers long enough to score as cross-file refs.
_IDENT = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{2,})\b")

# Boost common entry-ish names slightly.
_ENTRY_BONUS = frozenset(
    {
        "main",
        "Main",
        "App",
        "index",
        "run",
        "start",
        "bootstrap",
        "create",
        "setup",
        "init",
        "cli",
        "server",
        "application",
        "handler",
        "router",
    }
)


@dataclass(frozen=True)
class Symbol:
    name: str
    kind: str
    score: float = 0.0


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def map_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / REL_PATH


def exists(repo_root: Path | str) -> bool:
    return map_path(repo_root).is_file()


def list_source_files(
    repo_root: Path | str,
    *,
    max_files: int = DEFAULT_MAX_SCAN_FILES,
) -> list[Path]:
    root = Path(repo_root).resolve()
    if not root.is_dir():
        return []
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if any(part in IGNORE_DIRS or part.startswith(".") for part in rel_parts[:-1]):
            # allow dotted source files at leaf; skip hidden dirs
            continue
        if path.suffix.lower() not in SOURCE_EXTS:
            continue
        try:
            if path.stat().st_size > DEFAULT_MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        out.append(path)
        if len(out) >= max_files:
            break
    out.sort(key=lambda p: p.as_posix())
    return out


def extract_symbols(text: str, ext: str) -> list[Symbol]:
    """Extract definition names; ext reserved for future language-specific rules."""
    del ext  # patterns are multi-language
    seen: set[str] = set()
    found: list[Symbol] = []
    for pattern, kind in _SYMBOL_PATTERNS:
        for match in pattern.finditer(text or ""):
            name = match.group(1)
            if name in seen or name.startswith("_"):
                continue
            # skip dunder / tiny noise
            if name in {"self", "cls", "args", "kwargs"}:
                continue
            seen.add(name)
            found.append(Symbol(name=name, kind=kind))
    return found


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _depth_penalty(rel: str) -> float:
    depth = rel.count("/")
    return max(0.0, 3.0 - depth) * 0.5


def rank_map(
    repo_root: Path | str,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_symbols: int = DEFAULT_MAX_SYMBOLS,
    max_scan_files: int = DEFAULT_MAX_SCAN_FILES,
) -> list[dict]:
    """Return ranked [{path, score, symbols:[{name,kind,score}]}] relative paths."""
    root = Path(repo_root).resolve()
    files = list_source_files(root, max_files=max_scan_files)
    if not files:
        return []

    file_texts: dict[str, str] = {}
    file_symbols: dict[str, list[Symbol]] = {}
    all_names: set[str] = set()

    for path in files:
        rel = path.relative_to(root).as_posix()
        text = _read_text(path)
        file_texts[rel] = text
        syms = extract_symbols(text, path.suffix.lower())
        file_symbols[rel] = syms
        all_names.update(s.name for s in syms)

    # Global identifier frequency (poor man's reference graph).
    global_counts: dict[str, int] = {n: 0 for n in all_names}
    if all_names:
        # One pass per file over idents; only count known definition names.
        for text in file_texts.values():
            for m in _IDENT.finditer(text):
                name = m.group(1)
                if name in global_counts:
                    global_counts[name] += 1

    ranked: list[dict] = []
    for rel, syms in file_symbols.items():
        if not syms and not rel.endswith((".py", ".ts", ".js", ".go", ".rs")):
            # keep empty-ish only if source-y; still allow path-only rank later
            pass
        scored_syms: list[Symbol] = []
        file_score = _depth_penalty(rel)
        # Prefer shorter entry-ish basenames
        base = Path(rel).stem
        if base in _ENTRY_BONUS or base.lower() in {x.lower() for x in _ENTRY_BONUS}:
            file_score += 2.0
        for s in syms:
            # subtract 1 for the definition itself when possible
            refs = max(0, global_counts.get(s.name, 0) - 1)
            bonus = 1.5 if s.name in _ENTRY_BONUS else 0.0
            sc = float(refs) + bonus + (0.25 if s.kind in {"class", "struct", "type", "interface"} else 0.0)
            scored_syms.append(Symbol(name=s.name, kind=s.kind, score=sc))
            file_score += sc
        # files with no symbols still get tiny path score so map is not empty
        if not scored_syms:
            file_score += 0.1
        scored_syms.sort(key=lambda s: (-s.score, s.name))
        top = scored_syms[: max(0, max_symbols)]
        ranked.append(
            {
                "path": rel,
                "score": round(file_score, 3),
                "symbols": [
                    {"name": s.name, "kind": s.kind, "score": round(s.score, 3)} for s in top
                ],
            }
        )

    ranked.sort(key=lambda e: (-float(e["score"]), e["path"]))
    return ranked[: max(0, max_files)]


def render_from_ranked(
    ranked: Iterable[dict],
    *,
    max_chars: int = DEFAULT_MAP_MAX_CHARS,
    updated: str | None = None,
) -> str:
    lines = [
        "# Repo map",
        f"Updated: {updated or _utc_now()}",
        "",
        "Ranked paths + key symbols (sample). Pure heuristic rank — no AI.",
        "",
    ]
    for entry in ranked:
        path = entry.get("path") or ""
        lines.append(f"{path}:")
        syms = entry.get("symbols") or []
        if not syms:
            lines.append("  (no symbols)")
        else:
            for s in syms:
                kind = s.get("kind") or "sym"
                name = s.get("name") or ""
                lines.append(f"  {kind} {name}")
        lines.append("")
    text = "\n".join(lines).rstrip() + "\n"
    if len(text) > max_chars:
        text = text[: max(0, max_chars - 3)].rstrip() + "...\n"
    return text


def render(
    repo_root: Path | str,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_symbols: int = DEFAULT_MAX_SYMBOLS,
    max_chars: int = DEFAULT_MAP_MAX_CHARS,
) -> str:
    ranked = rank_map(repo_root, max_files=max_files, max_symbols=max_symbols)
    return render_from_ranked(ranked, max_chars=max_chars)


def write(
    repo_root: Path | str,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_symbols: int = DEFAULT_MAX_SYMBOLS,
    max_chars: int = DEFAULT_MAP_MAX_CHARS,
) -> Path:
    path = map_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render(
        repo_root,
        max_files=max_files,
        max_symbols=max_symbols,
        max_chars=max_chars,
    )
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
    tmp.replace(path)
    return path


def inject_snippet(
    repo_root: Path | str,
    *,
    max_chars: int = INJECT_MAX_CHARS,
) -> str:
    """Thin SessionStart block. Empty when no map file. Hard size cap."""
    path = map_path(repo_root)
    if not path.is_file():
        return ""
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    body = body.strip()
    if not body:
        return ""
    # Prefer a short header + top of file
    if not body.lower().startswith("# repo map"):
        body = "# Repo map\n" + body
    # Drop long banner lines for inject: keep path: + symbol lines only if huge
    snippet = "Repo map:\n" + body
    if len(snippet) > max_chars:
        snippet = snippet[: max(0, max_chars - 3)].rstrip() + "..."
    return snippet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a ranked repo map sample (no AI)."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="build",
        choices=["build", "show", "inject", "rank"],
        help="build|show|inject|rank (default: build)",
    )
    parser.add_argument("--json", action="store_true", help="JSON for rank/build meta")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--max-symbols", type=int, default=DEFAULT_MAX_SYMBOLS)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAP_MAX_CHARS)
    args = parser.parse_args(argv)

    root = Path(args.project).resolve()
    cmd = args.command

    if cmd == "rank":
        ranked = rank_map(
            root, max_files=args.max_files, max_symbols=args.max_symbols
        )
        if args.json:
            print(json.dumps(ranked, indent=2))
        else:
            for entry in ranked:
                syms = ", ".join(s["name"] for s in entry.get("symbols") or [])
                print(f"{entry['score']:.1f}\t{entry['path']}\t{syms}")
        return 0

    if cmd == "inject":
        snippet = inject_snippet(root)
        if snippet:
            print(snippet)
        return 0

    if cmd == "show":
        if not exists(root):
            print("(no repo-map file — run: build)", file=__import__("sys").stderr)
            return 1
        print(map_path(root).read_text(encoding="utf-8"), end="")
        return 0

    # build
    path = write(
        root,
        max_files=args.max_files,
        max_symbols=args.max_symbols,
        max_chars=args.max_chars,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "path": str(path),
                    "rel": REL_PATH.as_posix(),
                    "chars": path.stat().st_size,
                }
            )
        )
    else:
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
