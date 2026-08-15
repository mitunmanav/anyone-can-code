#!/usr/bin/env python3
"""ACC checkpoints — lightweight file list + hash snapshots.

Pattern only (inspired by Cline shadow-git idea). Not a real shadow git repo.
Does not touch the project's .git history.

Storage: `.codex/anyone-can-code/state/checkpoints/<id>/`
  meta.json   — id, label, created_at, file_count, skipped
  files.json  — [{path, sha256, size}]
  blobs/<sha256> — file bytes for restore

CLI: save | list | restore
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

NAMESPACE = Path(".codex") / "anyone-can-code"
CHECKPOINTS_REL = NAMESPACE / "state" / "checkpoints"

# Never walk these directory names (anywhere in the tree).
IGNORE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".codex",
    ".codegraph",
    ".grok",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    "coverage",
    ".idea",
    ".vscode",
}

# Skip content for huge files (still listed with sha when under hard cap).
MAX_BLOB_BYTES = 1_500_000
MAX_TOTAL_BLOB_BYTES = 40_000_000
MAX_FILES = 5_000


class CheckpointError(RuntimeError):
    """User-facing checkpoint failure."""


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def checkpoints_dir(repo_root: Path | str) -> Path:
    return Path(repo_root) / CHECKPOINTS_REL


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 64)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _safe_rel(path: Path, root: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    text = rel.as_posix()
    if text in {".", ""}:
        return None
    return text


def _should_skip_dir(name: str) -> bool:
    return name in IGNORE_DIR_NAMES or name.endswith(".egg-info")


def iter_project_files(
    repo_root: Path,
    paths: Iterable[str] | None = None,
) -> list[Path]:
    """Return absolute file paths under repo_root to snapshot."""
    root = Path(repo_root).resolve()
    if paths:
        out: list[Path] = []
        for raw in paths:
            p = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
            try:
                p.relative_to(root)
            except ValueError as exc:
                raise CheckpointError(f"path outside project: {raw}") from exc
            if p.is_file():
                out.append(p)
        return out

    found: list[Path] = []
    for dirpath, dirnames, filenames in root.walk() if hasattr(root, "walk") else _os_walk(root):
        # prune in-place
        dirnames[:] = sorted(d for d in dirnames if not _should_skip_dir(d))
        for name in sorted(filenames):
            if name in {".DS_Store", "Thumbs.db"}:
                continue
            found.append(Path(dirpath) / name)
            if len(found) >= MAX_FILES:
                return found
    return found


def _os_walk(root: Path):
    """Fallback walk for older Python (yields Path dirpath, dirnames, filenames)."""
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        yield Path(dirpath), dirnames, filenames


def _new_id() -> str:
    # time_ns keeps same-second saves ordered newest-first when sorting by id.
    ns = time.time_ns()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(ns / 1_000_000_000))
    short = uuid.uuid4().hex[:6]
    return f"cp-{stamp}-{ns}-{short}"


def save(
    repo_root: Path | str,
    *,
    label: str = "",
    paths: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Snapshot file list + hashes (+ blobs) under state/checkpoints/<id>/."""
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise CheckpointError(f"project root not a directory: {root}")

    cp_id = _new_id()
    entry = checkpoints_dir(root) / cp_id
    blobs = entry / "blobs"
    blobs.mkdir(parents=True, exist_ok=True)

    file_records: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    total_blob = 0

    for abs_path in iter_project_files(root, paths):
        rel = _safe_rel(abs_path, root)
        if not rel:
            continue
        # Never store the checkpoint store itself (also covered by IGNORE .codex)
        if rel.startswith(".codex/") or rel.startswith(".git/"):
            continue
        try:
            size = abs_path.stat().st_size
        except OSError as exc:
            skipped.append({"path": rel, "reason": f"stat: {exc}"})
            continue

        try:
            digest = sha256_file(abs_path)
        except OSError as exc:
            skipped.append({"path": rel, "reason": f"hash: {exc}"})
            continue

        record: dict[str, Any] = {
            "path": rel,
            "sha256": digest,
            "size": size,
            "stored": False,
        }

        if size > MAX_BLOB_BYTES:
            skipped.append({"path": rel, "reason": f"too large ({size} > {MAX_BLOB_BYTES})"})
            file_records.append(record)
            continue
        if total_blob + size > MAX_TOTAL_BLOB_BYTES:
            skipped.append({"path": rel, "reason": "blob budget full"})
            file_records.append(record)
            continue

        blob_path = blobs / digest
        if not blob_path.exists():
            try:
                data = abs_path.read_bytes()
                blob_path.write_bytes(data)
                total_blob += len(data)
            except OSError as exc:
                skipped.append({"path": rel, "reason": f"read: {exc}"})
                file_records.append(record)
                continue
        else:
            total_blob += size

        record["stored"] = True
        file_records.append(record)

    meta: dict[str, Any] = {
        "id": cp_id,
        "label": (label or "").strip(),
        "created_at": _utc_now(),
        "file_count": len(file_records),
        "stored_count": sum(1 for r in file_records if r.get("stored")),
        "skipped_count": len(skipped),
        "schema": 1,
        "kind": "acc-checkpoint",
        "note": "pattern-only snapshot (not Cline shadow-git)",
    }

    (entry / "meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (entry / "files.json").write_text(
        json.dumps(file_records, indent=2) + "\n", encoding="utf-8"
    )
    if skipped:
        (entry / "skipped.json").write_text(
            json.dumps(skipped, indent=2) + "\n", encoding="utf-8"
        )

    # Maintain a small index for list speed
    _update_index(root, meta)
    return meta


def _update_index(repo_root: Path, meta: dict[str, Any]) -> None:
    index_path = checkpoints_dir(repo_root) / "index.json"
    items: list[dict[str, Any]] = []
    if index_path.is_file():
        try:
            raw = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                items = [x for x in raw if isinstance(x, dict)]
        except (OSError, json.JSONDecodeError):
            items = []
    items = [x for x in items if x.get("id") != meta.get("id")]
    items.append(
        {
            "id": meta["id"],
            "label": meta.get("label") or "",
            "created_at": meta.get("created_at") or "",
            "file_count": meta.get("file_count") or 0,
        }
    )
    # Newest first: id embeds time+ms; created_at is second-granularity only.
    items.sort(
        key=lambda x: (x.get("id") or "", x.get("created_at") or ""),
        reverse=True,
    )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")


def list_checkpoints(repo_root: Path | str) -> list[dict[str, Any]]:
    """Return checkpoint summaries, newest first."""
    root = Path(repo_root).resolve()
    base = checkpoints_dir(root)
    if not base.is_dir():
        return []

    index_path = base / "index.json"
    if index_path.is_file():
        try:
            raw = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(raw, list) and raw:
                return [x for x in raw if isinstance(x, dict) and x.get("id")]
        except (OSError, json.JSONDecodeError):
            pass

    items: list[dict[str, Any]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(meta, dict) or not meta.get("id"):
            continue
        items.append(
            {
                "id": meta["id"],
                "label": meta.get("label") or "",
                "created_at": meta.get("created_at") or "",
                "file_count": meta.get("file_count") or 0,
            }
        )
    items.sort(
        key=lambda x: (x.get("id") or "", x.get("created_at") or ""),
        reverse=True,
    )
    return items


def _load_entry(repo_root: Path, checkpoint_id: str) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    entry = checkpoints_dir(repo_root) / checkpoint_id
    meta_path = entry / "meta.json"
    files_path = entry / "files.json"
    if not meta_path.is_file() or not files_path.is_file():
        raise CheckpointError(f"checkpoint not found: {checkpoint_id}")
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        files = json.loads(files_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckpointError(f"corrupt checkpoint: {checkpoint_id}") from exc
    if not isinstance(meta, dict) or not isinstance(files, list):
        raise CheckpointError(f"corrupt checkpoint: {checkpoint_id}")
    return entry, meta, files


def restore(
    repo_root: Path | str,
    checkpoint_id: str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Restore stored files from a checkpoint. Does not delete extra files."""
    root = Path(repo_root).resolve()
    if not re.fullmatch(r"cp-[A-Za-z0-9._-]+", checkpoint_id or ""):
        # still allow lookup if folder exists with odd id from older versions
        if not (checkpoints_dir(root) / (checkpoint_id or "")).is_dir():
            raise CheckpointError(f"checkpoint not found: {checkpoint_id}")

    entry, meta, files = _load_entry(root, checkpoint_id)
    blobs = entry / "blobs"
    restored = 0
    missing_blob = 0
    unchanged = 0
    details: list[dict[str, str]] = []

    for rec in files:
        if not isinstance(rec, dict):
            continue
        rel = str(rec.get("path") or "").strip()
        digest = str(rec.get("sha256") or "").strip()
        if not rel or not digest:
            continue
        # path safety
        target = (root / rel).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            details.append({"path": rel, "status": "outside-root-skipped"})
            continue
        if rel.startswith(".git/") or rel == ".git":
            details.append({"path": rel, "status": "git-skipped"})
            continue

        blob = blobs / digest
        if not blob.is_file():
            missing_blob += 1
            details.append({"path": rel, "status": "no-blob"})
            continue

        data = blob.read_bytes()
        if target.is_file():
            try:
                if sha256_file(target) == digest:
                    unchanged += 1
                    continue
            except OSError:
                pass

        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".acc-cp.tmp")
            tmp.write_bytes(data)
            tmp.replace(target)
        restored += 1
        details.append({"path": rel, "status": "restored"})

    return {
        "id": meta.get("id") or checkpoint_id,
        "label": meta.get("label") or "",
        "restored": restored,
        "unchanged": unchanged,
        "missing_blob": missing_blob,
        "dry_run": dry_run,
        "file_count": len(files),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC checkpoints: save / list / restore file list+hash snapshots."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _add_json(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--json",
            action="store_true",
            help="Emit JSON",
        )

    p_save = sub.add_parser("save", help="Snapshot current files")
    _add_json(p_save)
    p_save.add_argument("--label", default="", help="Optional label")
    p_save.add_argument(
        "--path",
        action="append",
        dest="paths",
        default=None,
        help="Relative path to include (repeatable). Default: walk project.",
    )

    p_list = sub.add_parser("list", help="List checkpoints (newest first)")
    _add_json(p_list)

    p_restore = sub.add_parser("restore", help="Restore files from a checkpoint id")
    _add_json(p_restore)
    p_restore.add_argument("id", help="Checkpoint id (cp-...)")
    p_restore.add_argument(
        "--dry-run",
        action="store_true",
        help="Report only; do not write files",
    )

    args = parser.parse_args(argv)
    root = Path(args.project).resolve()

    try:
        if args.cmd == "save":
            meta = save(root, label=args.label, paths=args.paths)
            if args.json:
                print(json.dumps(meta, indent=2))
            else:
                print(
                    f"saved {meta['id']} files={meta['file_count']} "
                    f"stored={meta['stored_count']} label={meta.get('label') or '-'}"
                )
            return 0

        if args.cmd == "list":
            items = list_checkpoints(root)
            if args.json:
                print(json.dumps(items, indent=2))
            else:
                if not items:
                    print("(no checkpoints)")
                for item in items:
                    print(
                        f"{item['id']}  files={item.get('file_count', 0)}  "
                        f"{item.get('created_at', '')}  {item.get('label') or ''}"
                    )
            return 0

        if args.cmd == "restore":
            result = restore(root, args.id, dry_run=bool(args.dry_run))
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(
                    f"restore {result['id']} restored={result['restored']} "
                    f"unchanged={result['unchanged']} missing_blob={result['missing_blob']}"
                )
            return 0
    except CheckpointError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
