#!/usr/bin/env python3
"""Progress ledger — fight context rot.

On-disk truth under `.codex/anyone-can-code/state/progress-ledger.md`:
WHERE / NEXT / DONE / OPEN.

API used by `$ledger` skill, SessionStart inject (thin), PreCompact/save
capsule pointers. Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from typing import Any

REL_PATH = Path(".codex/anyone-can-code/state/progress-ledger.md")
INJECT_MAX_CHARS = 320
MAX_DONE_KEEP = 12
MAX_OPEN_KEEP = 12
MAX_LINE = 200


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _clip(text: str, n: int = MAX_LINE) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= n:
        return text
    return text[: max(0, n - 3)].rstrip() + "..."


def ledger_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / REL_PATH


def exists(repo_root: Path | str) -> bool:
    return ledger_path(repo_root).is_file()


def _empty_data() -> dict[str, Any]:
    return {
        "updated": _utc_now(),
        "where": "",
        "next": "",
        "done": [],
        "open": [],
        "notes": [],
    }


def _bullet_body(line: str) -> str:
    s = line.strip()
    if s.startswith("- [x]") or s.startswith("- [X]"):
        return s[5:].strip()
    if s.startswith("- [ ]"):
        return s[5:].strip()
    if s.startswith("- "):
        return s[2:].strip()
    return s


def load(repo_root: Path | str) -> dict[str, Any]:
    """Parse progress-ledger.md → {where, next, done, open, notes, updated}."""
    path = ledger_path(repo_root)
    data = _empty_data()
    if not path.is_file():
        return data
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return data
    section = ""
    where_lines: list[str] = []
    next_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("Updated:"):
            data["updated"] = stripped.split(":", 1)[1].strip() or data["updated"]
            continue
        if stripped.startswith("## "):
            section = stripped[3:].strip().upper()
            continue
        if not stripped or stripped.startswith("# "):
            continue
        if section == "WHERE":
            where_lines.append(stripped)
        elif section == "NEXT":
            next_lines.append(stripped)
        elif section == "DONE":
            body = _bullet_body(stripped)
            if body and body.lower() not in {"(none yet)", "(none)"}:
                data["done"].append(body)
        elif section == "OPEN":
            body = _bullet_body(stripped)
            if body and body.lower() not in {"(none yet)", "(none)"}:
                data["open"].append(body)
        elif section == "NOTES":
            body = _bullet_body(stripped)
            if body and body.lower() not in {"(none yet)", "(none)"}:
                data["notes"].append(body)
    data["where"] = _clip(" ".join(where_lines), 400) if where_lines else ""
    data["next"] = _clip(" ".join(next_lines), 400) if next_lines else ""
    return data


def render_from_data(data: dict[str, Any]) -> str:
    done = list(data.get("done") or [])[-MAX_DONE_KEEP:]
    open_items = list(data.get("open") or [])[-MAX_OPEN_KEEP:]
    notes = list(data.get("notes") or [])[-8:]
    lines = [
        "# Progress Ledger",
        f"Updated: {data.get('updated') or _utc_now()}",
        "",
        "## WHERE",
        _clip(str(data.get("where") or "not set"), 400) or "not set",
        "",
        "## NEXT",
        _clip(str(data.get("next") or "not set"), 400) or "not set",
        "",
        "## DONE",
    ]
    if done:
        lines.extend(f"- [x] {_clip(item)}" for item in done)
    else:
        lines.append("- (none yet)")
    lines += ["", "## OPEN"]
    if open_items:
        lines.extend(f"- [ ] {_clip(item)}" for item in open_items)
    else:
        lines.append("- (none)")
    if notes:
        lines += ["", "## NOTES"]
        lines.extend(f"- {_clip(n)}" for n in notes)
    lines.append("")
    return "\n".join(lines)


def render(repo_root: Path | str) -> str:
    if not exists(repo_root):
        return ""
    return render_from_data(load(repo_root))


def _write(repo_root: Path | str, data: dict[str, Any]) -> Path:
    path = ledger_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dict(data)
    data["updated"] = _utc_now()
    data["done"] = list(data.get("done") or [])[-MAX_DONE_KEEP:]
    data["open"] = list(data.get("open") or [])[-MAX_OPEN_KEEP:]
    text = render_from_data(data)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
    tmp.replace(path)
    return path


def init(
    repo_root: Path | str,
    *,
    where: str = "",
    next_step: str = "",
    force: bool = False,
) -> Path:
    """Create ledger if missing (or force rewrite headers while keeping lists)."""
    path = ledger_path(repo_root)
    if path.is_file() and not force:
        data = load(repo_root)
        if where:
            data["where"] = _clip(where, 400)
        if next_step:
            data["next"] = _clip(next_step, 400)
        return _write(repo_root, data)
    data = _empty_data()
    data["where"] = _clip(where, 400) if where else "not set"
    data["next"] = _clip(next_step, 400) if next_step else "not set"
    return _write(repo_root, data)


def set_where(repo_root: Path | str, where: str) -> Path:
    if not exists(repo_root):
        return init(repo_root, where=where)
    data = load(repo_root)
    data["where"] = _clip(where, 400)
    return _write(repo_root, data)


def set_next(repo_root: Path | str, next_step: str) -> Path:
    if not exists(repo_root):
        return init(repo_root, next_step=next_step)
    data = load(repo_root)
    data["next"] = _clip(next_step, 400)
    return _write(repo_root, data)


def append_done(repo_root: Path | str, item: str) -> Path:
    item = _clip(item)
    if not item:
        return ledger_path(repo_root)
    if not exists(repo_root):
        init(repo_root)
    data = load(repo_root)
    # drop from open if same text
    data["open"] = [x for x in data["open"] if x != item]
    if item not in data["done"]:
        data["done"].append(item)
    return _write(repo_root, data)


def append_open(repo_root: Path | str, item: str) -> Path:
    item = _clip(item)
    if not item:
        return ledger_path(repo_root)
    if not exists(repo_root):
        init(repo_root)
    data = load(repo_root)
    if item not in data["open"] and item not in data["done"]:
        data["open"].append(item)
    return _write(repo_root, data)


def append_capsule_pointer(
    repo_root: Path | str,
    *,
    pointer: str,
    note: str = "",
) -> Path:
    """Record a compact/session capsule pointer in NOTES (and soft OPEN hint)."""
    pointer = _clip(pointer, 160)
    note = _clip(note, 80)
    if not pointer:
        return ledger_path(repo_root)
    if not exists(repo_root):
        init(repo_root)
    data = load(repo_root)
    stamp = _utc_now()
    entry = f"capsule {stamp}: {pointer}"
    if note:
        entry = f"{entry} ({note})"
    notes = list(data.get("notes") or [])
    # de-dupe exact pointer lines (keep latest)
    notes = [n for n in notes if pointer not in n]
    notes.append(entry)
    data["notes"] = notes[-8:]
    return _write(repo_root, data)


def inject_line(repo_root: Path | str, max_chars: int = INJECT_MAX_CHARS) -> str:
    """Thin SessionStart block. Empty when no ledger. Hard size cap."""
    if not exists(repo_root):
        return ""
    data = load(repo_root)
    where = _clip(str(data.get("where") or ""), 80)
    nxt = _clip(str(data.get("next") or ""), 80)
    n_open = len(data.get("open") or [])
    n_done = len(data.get("done") or [])
    bits: list[str] = []
    if where and where != "not set":
        bits.append(f"WHERE={where}")
    if nxt and nxt != "not set":
        bits.append(f"NEXT={nxt}")
    bits.append(f"done={n_done} open={n_open}")
    bits.append(f"file={REL_PATH.as_posix()}")
    line = "Ledger: " + " | ".join(bits)
    if len(line) > max_chars:
        line = line[: max(0, max_chars - 3)].rstrip() + "..."
    return line


def sync_from_workflow(repo_root: Path | str, workflow: dict[str, Any] | None) -> Path | None:
    """Optional: refresh WHERE/NEXT from workflow when ledger already exists."""
    if not exists(repo_root) or not workflow:
        return None
    where = str(
        workflow.get("active_goal")
        or workflow.get("active_task")
        or workflow.get("last_task")
        or ""
    ).strip()
    nxt = str(
        workflow.get("next_action") or workflow.get("next_step") or ""
    ).strip()
    data = load(repo_root)
    changed = False
    if where and where != data.get("where"):
        data["where"] = _clip(where, 400)
        changed = True
    if nxt and nxt != data.get("next"):
        data["next"] = _clip(nxt, 400)
        changed = True
    if not changed:
        return ledger_path(repo_root)
    return _write(repo_root, data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ACC progress ledger (context rot)")
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create or update WHERE/NEXT")
    p_init.add_argument("--where", default="")
    p_init.add_argument("--next", dest="next_step", default="")
    p_init.add_argument("--force", action="store_true")

    p_where = sub.add_parser("where", help="Set WHERE")
    p_where.add_argument("text")

    p_next = sub.add_parser("next", help="Set NEXT")
    p_next.add_argument("text")

    p_done = sub.add_parser("done", help="Append DONE item")
    p_done.add_argument("text")

    p_open = sub.add_parser("open", help="Append OPEN item")
    p_open.add_argument("text")

    p_cap = sub.add_parser("capsule", help="Append capsule pointer")
    p_cap.add_argument("pointer")
    p_cap.add_argument("--note", default="")

    sub.add_parser("show", help="Print full ledger")
    sub.add_parser("inject", help="Print SessionStart inject line")
    sub.add_parser("path", help="Print ledger path")

    args = parser.parse_args(argv)
    root = Path(args.project).resolve()

    if args.cmd == "init":
        path = init(root, where=args.where, next_step=args.next_step, force=args.force)
        print(path)
        return 0
    if args.cmd == "where":
        print(set_where(root, args.text))
        return 0
    if args.cmd == "next":
        print(set_next(root, args.text))
        return 0
    if args.cmd == "done":
        print(append_done(root, args.text))
        return 0
    if args.cmd == "open":
        print(append_open(root, args.text))
        return 0
    if args.cmd == "capsule":
        print(append_capsule_pointer(root, pointer=args.pointer, note=args.note))
        return 0
    if args.cmd == "show":
        print(render(root), end="")
        return 0
    if args.cmd == "inject":
        print(inject_line(root))
        return 0
    if args.cmd == "path":
        print(ledger_path(root))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
