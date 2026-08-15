#!/usr/bin/env python3
"""You-Brain v1 — one-shot local mine of Codex rollout-*.jsonl.

No model API. No embedder. Stream-parse only.
Default = dry-run preview. Apply YOU.md only with --apply.

Layers (MEMORY-CONTRACT drawers):
  L1 raw facts  → <memory-root>/you-brain/raw/facts.jsonl  (append-only)
  L2 aggregates → <memory-root>/you-brain/aggregates/*.json  (rebuildable)
  L3 applied    → <memory-root>/you-brain/YOU.md  (--apply only)
  Preview always → <memory-root>/you-brain/YOU.preview.md

Default memory-root = user drawer ~/.codex/anyone-can-code/user-memory
(override ACC_USER_MEMORY_ROOT or --memory-root). Project facts stay out.

Native Codex memories stay OFF — ACC wiki/drawers only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

# Optional soft tip (same package)
try:
    import model_ledger as _model_ledger
except ImportError:  # pragma: no cover - path insert fallback
    _here = Path(__file__).resolve().parent
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    try:
        import model_ledger as _model_ledger
    except ImportError:
        _model_ledger = None  # type: ignore

SCHEMA_VERSION = 1
DEFAULT_MAX_FILES = 40
DEFAULT_MAX_MB = 256
DEFAULT_MAX_LINES_PER_FILE = 50_000
FACTS_NAME = "facts.jsonl"
INDEX_NAME = "ingest-index.json"
PREVIEW_NAME = "YOU.preview.md"
APPLIED_NAME = "YOU.md"

# Cheap task signals from user text (rules only — no AI)
_TASK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bug-fix", re.compile(r"\b(bug|fix|broken|crash|error|fail(ed|ure)?)\b", re.I)),
    ("feature", re.compile(r"\b(feature|add|implement|build|ship)\b", re.I)),
    ("plan", re.compile(r"\b(plan|design|architect|roadmap)\b", re.I)),
    ("research", re.compile(r"\b(research|investigate|explore|audit)\b", re.I)),
    ("test", re.compile(r"\b(test|pytest|unit test|e2e)\b", re.I)),
    ("refactor", re.compile(r"\b(refactor|cleanup|clean up|tidy)\b", re.I)),
    ("docs", re.compile(r"\b(docs?|readme|documentation)\b", re.I)),
    ("setup", re.compile(r"\b(setup|install|bootstrap|onboard)\b", re.I)),
]

_USER_CORRECTION = (
    "you were wrong",
    "that is wrong",
    "don't do that",
    "do not ",
    "never ",
    "always use",
    "stop doing",
    "wrong again",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_dirs() -> list[Path]:
    """Discover Codex session roots: CODEX_HOME then ~/.codex/sessions."""
    dirs: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        dirs.append(Path(codex_home) / "sessions")
    dirs.append(Path.home() / ".codex" / "sessions")
    seen: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def default_memory_root() -> Path:
    env = os.environ.get("ACC_USER_MEMORY_ROOT", "").strip()
    if env:
        return Path(env)
    return Path.home() / ".codex" / "anyone-can-code" / "user-memory"


def you_brain_dir(memory_root: Path) -> Path:
    return Path(memory_root) / "you-brain"


def list_rollouts(
    roots: list[Path] | None = None,
    *,
    limit: int = DEFAULT_MAX_FILES,
) -> list[Path]:
    roots = roots if roots is not None else session_dirs()
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            found.extend(root.rglob("rollout-*.jsonl"))
        except OSError:
            continue
    found.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return found[: max(0, limit)]


def _file_fingerprint(path: Path) -> dict[str, Any]:
    st = path.stat()
    return {
        "path": str(path.resolve()) if path.exists() else str(path),
        "mtime": st.st_mtime,
        "size": st.st_size,
    }


def _skip_unchanged(fp: dict[str, Any], index: dict[str, Any]) -> bool:
    files = index.get("files") or {}
    prev = files.get(fp["path"])
    if not prev:
        return False
    return (
        float(prev.get("mtime") or 0) == float(fp["mtime"])
        and int(prev.get("size") or -1) == int(fp["size"])
    )


def load_ingest_index(brain: Path) -> dict[str, Any]:
    path = brain / INDEX_NAME
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": SCHEMA_VERSION, "files": {}}
    if not isinstance(data, dict):
        return {"schema_version": SCHEMA_VERSION, "files": {}}
    data.setdefault("files", {})
    data["schema_version"] = SCHEMA_VERSION
    return data


def save_ingest_index(brain: Path, index: dict[str, Any]) -> None:
    brain.mkdir(parents=True, exist_ok=True)
    path = brain / INDEX_NAME
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def iter_jsonl_lines(path: Path, *, max_lines: int) -> Iterator[dict[str, Any]]:
    """Stream-parse JSONL; skip corrupt lines. No full-file load required."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh):
                if i >= max_lines:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    yield obj
    except OSError:
        return


def _text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        bits: list[str] = []
        for part in content:
            if isinstance(part, dict):
                bits.append(str(part.get("text") or ""))
            else:
                bits.append(str(part))
        return " ".join(bits)
    return ""


def _extract_user_texts(entry: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    etype = entry.get("type")
    payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}

    if etype == "event_msg" and payload.get("type") == "user_message":
        msg = payload.get("message") or payload.get("text") or ""
        if msg:
            texts.append(str(msg))
    if etype == "response_item" and payload.get("type") == "message":
        role = str(payload.get("role") or "").lower()
        if role == "user":
            t = _text_from_content(payload.get("content"))
            if t:
                texts.append(t)
    return texts


def _task_signals_from_text(text: str) -> list[str]:
    hits: list[str] = []
    for name, pat in _TASK_PATTERNS:
        if pat.search(text):
            hits.append(name)
    return hits


def _has_correction(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _USER_CORRECTION)


def parse_rollout_stream(
    path: Path,
    *,
    max_lines: int = DEFAULT_MAX_LINES_PER_FILE,
) -> dict[str, Any] | None:
    """Extract session facts from one rollout file. Corrupt-safe."""
    session_id = ""
    model = ""
    effort = ""
    cwd = ""
    originator = ""
    models_seen: Counter[str] = Counter()
    efforts_seen: Counter[str] = Counter()
    task_signals: Counter[str] = Counter()
    user_msgs = 0
    correction_hits = 0
    last_tokens: dict[str, int] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_output_tokens": 0,
        "total_tokens": 0,
    }
    peak_total = 0
    lines_ok = 0
    lines_bad_skip = 0  # counted only as skipped via parse; stream hides bad
    saw_codex = False

    for entry in iter_jsonl_lines(path, max_lines=max_lines):
        lines_ok += 1
        etype = entry.get("type") or ""
        payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}

        if etype == "session_meta":
            saw_codex = True
            session_id = str(
                payload.get("session_id") or payload.get("id") or session_id or path.stem
            )
            cwd = str(payload.get("cwd") or cwd)
            originator = str(payload.get("originator") or originator)
            m = str(payload.get("model") or payload.get("agent_type") or "").strip()
            if m:
                model = m
                models_seen[m] += 1

        elif etype == "turn_context":
            saw_codex = True
            m = str(payload.get("model") or "").strip()
            if m:
                model = m or model
                models_seen[m] += 1
            cm = payload.get("collaboration_mode") if isinstance(payload.get("collaboration_mode"), dict) else {}
            settings = cm.get("settings") if isinstance(cm.get("settings"), dict) else {}
            reff = str(
                settings.get("reasoning_effort")
                or payload.get("reasoning_effort")
                or payload.get("model_reasoning_effort")
                or ""
            ).strip().lower()
            if reff:
                effort = reff
                efforts_seen[reff] += 1
            if not session_id and payload.get("turn_id"):
                # keep empty; prefer session_meta
                pass

        elif etype == "event_msg":
            ptype = payload.get("type")
            if ptype == "token_count":
                saw_codex = True
                info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
                total = info.get("total_token_usage") if isinstance(info.get("total_token_usage"), dict) else {}
                last = info.get("last_token_usage") if isinstance(info.get("last_token_usage"), dict) else {}
                src = last or total
                if src:
                    def _i(k: str) -> int:
                        try:
                            return int(src.get(k) or 0)
                        except (TypeError, ValueError):
                            return 0

                    last_tokens = {
                        "input_tokens": _i("input_tokens"),
                        "output_tokens": _i("output_tokens"),
                        "cached_input_tokens": _i("cached_input_tokens"),
                        "reasoning_output_tokens": _i("reasoning_output_tokens"),
                        "total_tokens": _i("total_tokens"),
                    }
                    peak_total = max(peak_total, last_tokens["total_tokens"])
            elif ptype == "user_message":
                saw_codex = True

        for text in _extract_user_texts(entry):
            text = text.strip()
            if not text:
                continue
            user_msgs += 1
            for sig in _task_signals_from_text(text):
                task_signals[sig] += 1
            if _has_correction(text):
                correction_hits += 1

    if not saw_codex and lines_ok == 0:
        return None
    if not session_id:
        # derive from filename rollout-...-UUID.jsonl
        m = re.search(
            r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
            path.name,
            re.I,
        )
        session_id = m.group(1) if m else path.stem

    if not model and models_seen:
        model = models_seen.most_common(1)[0][0]
    if not effort and efforts_seen:
        effort = efforts_seen.most_common(1)[0][0]

    return {
        "kind": "session_summary",
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "source_path": str(path),
        "model": model or "unknown",
        "reasoning_effort": effort or "",
        "models_seen": dict(models_seen),
        "efforts_seen": dict(efforts_seen),
        "tokens": last_tokens,
        "peak_total_tokens": peak_total,
        "task_signals": dict(task_signals),
        "user_message_count": user_msgs,
        "user_correction_hits": correction_hits,
        "cwd": cwd,
        "originator": originator,
        "lines_parsed": lines_ok,
        "lines_bad_skip": lines_bad_skip,
    }


def append_l1_fact(brain: Path, fact: dict[str, Any]) -> Path:
    raw_dir = brain / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / FACTS_NAME
    row = dict(fact)
    row["mined_at"] = utc_now()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def load_l1_facts(brain: Path) -> list[dict[str, Any]]:
    path = brain / "raw" / FACTS_NAME
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def build_aggregates(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """L2 rebuildable aggregates from L1 facts."""
    models: Counter[str] = Counter()
    efforts: Counter[str] = Counter()
    tasks: Counter[str] = Counter()
    model_task: dict[str, Counter[str]] = defaultdict(Counter)
    sessions = 0
    corrections = 0
    token_sum = 0
    by_session: dict[str, dict[str, Any]] = {}

    for f in facts:
        if f.get("kind") not in (None, "session_summary"):
            # accept session_summary or legacy missing kind
            if f.get("kind") and f.get("kind") != "session_summary":
                continue
        sessions += 1
        sid = str(f.get("session_id") or "")
        model = str(f.get("model") or "unknown")
        effort = str(f.get("reasoning_effort") or "") or "unknown"
        models[model] += 1
        if effort:
            efforts[effort] += 1
        corrections += int(f.get("user_correction_hits") or 0)
        toks = f.get("tokens") if isinstance(f.get("tokens"), dict) else {}
        try:
            token_sum += int(toks.get("total_tokens") or f.get("peak_total_tokens") or 0)
        except (TypeError, ValueError):
            pass
        sigs = f.get("task_signals") or {}
        if isinstance(sigs, dict):
            for k, v in sigs.items():
                try:
                    n = int(v)
                except (TypeError, ValueError):
                    n = 1
                tasks[str(k)] += n
                model_task[str(k)][model] += n
        if sid:
            by_session[sid] = {
                "model": model,
                "reasoning_effort": effort if effort != "unknown" else "",
                "task_signals": list(sigs.keys()) if isinstance(sigs, dict) else [],
            }

    top_model = models.most_common(1)[0][0] if models else "unknown"
    top_effort = efforts.most_common(1)[0][0] if efforts else "medium"
    if top_effort == "unknown":
        top_effort = "medium"

    return {
        "schema_version": SCHEMA_VERSION,
        "built_at": utc_now(),
        "sessions": sessions,
        "unique_sessions": len(by_session),
        "models": dict(models),
        "efforts": dict(efforts),
        "task_signals": dict(tasks),
        "model_by_task": {t: dict(c) for t, c in model_task.items()},
        "top_model": top_model,
        "top_effort": top_effort if top_effort != "unknown" else "medium",
        "user_correction_hits": corrections,
        "token_sum_last": token_sum,
        "by_session": by_session,
    }


def write_aggregates(brain: Path, agg: dict[str, Any]) -> Path:
    out_dir = brain / "aggregates"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # slim siblings for consumers
    (out_dir / "models.json").write_text(
        json.dumps(agg.get("models") or {}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "tasks.json").write_text(
        json.dumps(agg.get("task_signals") or {}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def soft_model_tips(
    agg: dict[str, Any],
    *,
    ledger_path: Path | None = None,
    min_n: int = 2,
) -> list[dict[str, Any]]:
    """Soft tips only — include n + confidence. Never hard default override."""
    tips: list[dict[str, Any]] = []
    task_signals = agg.get("task_signals") or {}
    model_by_task = agg.get("model_by_task") or {}

    # Prefer ledger when present
    for task, hits in sorted(task_signals.items(), key=lambda kv: -int(kv[1] or 0)):
        n_mine = int(hits or 0)
        model = ""
        reason = "mine aggregate"
        n = n_mine
        if _model_ledger is not None and ledger_path is not None:
            try:
                rec = _model_ledger.recommend_model(task, ledger_path=ledger_path)
                # count ledger rows for this task
                records = [
                    r
                    for r in _model_ledger._load_records(ledger_path)  # noqa: SLF001
                    if r.get("task_type") == task
                ]
                if records:
                    n = len(records)
                    model = str(rec.get("model") or "")
                    reason = f"ledger: {rec.get('reason') or 'scored'}"
            except Exception:
                pass
        if not model:
            per = model_by_task.get(task) or {}
            if per:
                model = max(per, key=lambda m: per[m])
                reason = "mine model×task counts"
            else:
                model = str(agg.get("top_model") or "unknown")
                reason = "mine top model"
        if n < min_n:
            continue
        # conf: soft curve, caps at 0.85 — never claim certainty
        conf = round(min(0.85, n / (n + 3)), 2)
        effort = "medium"
        if _model_ledger is not None:
            try:
                effort = _model_ledger.recommend_reasoning(task)
            except Exception:
                effort = str(agg.get("top_effort") or "medium")
        else:
            effort = str(agg.get("top_effort") or "medium")
        tips.append(
            {
                "task_type": task,
                "model": model,
                "reasoning": effort,
                "n": n,
                "confidence": conf,
                "reason": reason,
                "soft": True,
            }
        )
    # Global soft tip when no per-task
    if not tips and int(agg.get("sessions") or 0) >= min_n:
        n = int(agg.get("sessions") or 0)
        conf = round(min(0.85, n / (n + 3)), 2)
        tips.append(
            {
                "task_type": "general",
                "model": str(agg.get("top_model") or "unknown"),
                "reasoning": str(agg.get("top_effort") or "medium"),
                "n": n,
                "confidence": conf,
                "reason": "mine top overall",
                "soft": True,
            }
        )
    return tips[:8]


def render_you_md(
    agg: dict[str, Any],
    tips: list[dict[str, Any]],
    *,
    applied: bool,
    receipt: dict[str, Any] | None = None,
) -> str:
    status = "APPLIED" if applied else "PREVIEW (dry-run — not applied)"
    lines = [
        "# YOU — You-Brain v1",
        "",
        f"> Status: **{status}**",
        f"> Built: {agg.get('built_at') or utc_now()}",
        "> Native Codex memories: **OFF**. ACC two-drawer only.",
        "> No embedder. No model API during mine.",
        "",
        "## Snapshot",
        "",
        f"- Sessions fact rows: {agg.get('sessions', 0)}",
        f"- Unique sessions: {agg.get('unique_sessions', 0)}",
        f"- Top model: `{agg.get('top_model') or 'unknown'}`",
        f"- Common effort: `{agg.get('top_effort') or 'medium'}`",
        f"- User correction hits: {agg.get('user_correction_hits', 0)}",
        "",
        "## Models seen",
        "",
    ]
    models = agg.get("models") or {}
    if models:
        for m, c in sorted(models.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{m}` × {c}")
    else:
        lines.append("- (none yet)")
    lines += ["", "## Task signals", ""]
    tasks = agg.get("task_signals") or {}
    if tasks:
        for t, c in sorted(tasks.items(), key=lambda kv: -int(kv[1] or 0)):
            lines.append(f"- `{t}` × {c}")
    else:
        lines.append("- (none yet)")
    lines += [
        "",
        "## Soft model tips (advisory only)",
        "",
        "Never auto-switch model. Show n + confidence. User choice wins.",
        "",
    ]
    if tips:
        for tip in tips:
            lines.append(
                f"- **{tip['task_type']}** → `{tip['model']}` effort=`{tip['reasoning']}` "
                f"(n={tip['n']}, conf={tip['confidence']}) — {tip.get('reason', '')}"
            )
    else:
        lines.append("- (not enough signal; n_min not met)")
    lines += [
        "",
        "## Hard locks",
        "",
        "- Dry-run default; apply only with explicit `--apply`",
        "- L1 raw is append-only; L2 rebuildable; L3 applied only after yes",
        "- Never dump full chat into SessionStart",
        "- Wipe anytime: delete `you-brain/` under user-memory",
        "",
    ]
    if receipt:
        lines += [
            "## Last mine receipt",
            "",
            f"- Files scanned: {receipt.get('files_scanned', 0)}",
            f"- Files mined: {receipt.get('files_mined', 0)}",
            f"- Files skipped (unchanged): {receipt.get('files_skipped', 0)}",
            f"- Budget stop: {receipt.get('budget_stop') or 'none'}",
            f"- Token cost (API): **0**",
            "",
        ]
    return "\n".join(lines) + "\n"


def write_preview(brain: Path, text: str) -> Path:
    brain.mkdir(parents=True, exist_ok=True)
    path = brain / PREVIEW_NAME
    path.write_text(text, encoding="utf-8")
    return path


def apply_you_md(brain: Path, text: str) -> Path:
    """Write L3 applied YOU.md. Explicit only."""
    brain.mkdir(parents=True, exist_ok=True)
    path = brain / APPLIED_NAME
    path.write_text(text, encoding="utf-8")
    return path


def write_receipt(brain: Path, receipt: dict[str, Any]) -> Path:
    imp = brain / "imports"
    imp.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = imp / f"receipt-{stamp}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def mine(
    *,
    sessions_roots: list[Path] | None = None,
    memory_root: Path | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_mb: float = DEFAULT_MAX_MB,
    max_lines_per_file: int = DEFAULT_MAX_LINES_PER_FILE,
    apply: bool = False,
    force: bool = False,
    ledger_path: Path | None = None,
    write_l1: bool = True,
) -> dict[str, Any]:
    """Run full mine pipeline. Default dry-run for L3; L1/L2 written for preview.

    write_l1=True always records new facts when files change (needed for preview
    aggregates). L3 YOU.md only when apply=True.
    """
    memory_root = Path(memory_root) if memory_root is not None else default_memory_root()
    brain = you_brain_dir(memory_root)
    brain.mkdir(parents=True, exist_ok=True)

    index = load_ingest_index(brain)
    paths = list_rollouts(sessions_roots, limit=max_files)
    budget_bytes = int(max_mb * 1024 * 1024)
    bytes_used = 0
    files_scanned = 0
    files_mined = 0
    files_skipped = 0
    files_corrupt = 0
    budget_stop = None
    new_facts: list[dict[str, Any]] = []

    for path in paths:
        files_scanned += 1
        try:
            fp = _file_fingerprint(path)
        except OSError:
            files_corrupt += 1
            continue
        size = int(fp["size"])
        if bytes_used + size > budget_bytes and files_mined > 0:
            budget_stop = f"max_mb={max_mb}"
            break
        if not force and _skip_unchanged(fp, index):
            files_skipped += 1
            continue
        fact = parse_rollout_stream(path, max_lines=max_lines_per_file)
        if fact is None:
            files_corrupt += 1
            continue
        fact["source_mtime"] = fp["mtime"]
        fact["source_size"] = fp["size"]
        # content fingerprint of path+size+mtime for index
        digest = hashlib.sha256(
            f"{fp['path']}|{fp['size']}|{fp['mtime']}".encode()
        ).hexdigest()[:16]
        fact["source_fingerprint"] = digest
        if write_l1:
            append_l1_fact(brain, fact)
        new_facts.append(fact)
        index.setdefault("files", {})[fp["path"]] = {
            "mtime": fp["mtime"],
            "size": fp["size"],
            "fingerprint": digest,
            "session_id": fact.get("session_id"),
            "ingested_at": utc_now(),
        }
        files_mined += 1
        bytes_used += size

    save_ingest_index(brain, index)

    # Aggregates from full L1 (rebuildable)
    all_facts = load_l1_facts(brain) if write_l1 else list(new_facts)
    # If dry path wrote nothing and L1 empty, use in-memory new_facts only
    if not all_facts:
        all_facts = list(new_facts)
    agg = build_aggregates(all_facts)
    write_aggregates(brain, agg)

    tips = soft_model_tips(agg, ledger_path=ledger_path)

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "mined_at": utc_now(),
        "memory_root": str(memory_root),
        "brain_dir": str(brain),
        "files_scanned": files_scanned,
        "files_mined": files_mined,
        "files_skipped": files_skipped,
        "files_corrupt": files_corrupt,
        "bytes_used": bytes_used,
        "budget_stop": budget_stop,
        "max_files": max_files,
        "max_mb": max_mb,
        "apply": apply,
        "token_cost_api": 0,
        "tips_count": len(tips),
        "sessions_in_agg": agg.get("sessions"),
    }
    write_receipt(brain, receipt)

    preview_body = render_you_md(agg, tips, applied=False, receipt=receipt)
    preview_path = write_preview(brain, preview_body)
    applied_path = None
    if apply:
        applied_body = render_you_md(agg, tips, applied=True, receipt=receipt)
        applied_path = apply_you_md(brain, applied_body)

    return {
        "ok": True,
        "token_cost": 0,
        "memory_root": str(memory_root),
        "brain_dir": str(brain),
        "preview_path": str(preview_path),
        "applied_path": str(applied_path) if applied_path else None,
        "applied": apply,
        "receipt": receipt,
        "aggregates": {
            "sessions": agg.get("sessions"),
            "top_model": agg.get("top_model"),
            "top_effort": agg.get("top_effort"),
            "task_signals": agg.get("task_signals"),
        },
        "tips": tips,
        "message": (
            f"You-Brain mine: scanned={files_scanned} mined={files_mined} "
            f"skipped={files_skipped} apply={apply} api_tokens=0"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="You-Brain v1: mine Codex rollout jsonl (no AI, dry-run default)"
    )
    parser.add_argument(
        "--sessions-root",
        action="append",
        default=[],
        help="Sessions root (repeatable). Default: CODEX_HOME/sessions + ~/.codex/sessions",
    )
    parser.add_argument(
        "--memory-root",
        type=str,
        default="",
        help="User-memory root (default ACC_USER_MEMORY_ROOT or ~/.codex/anyone-can-code/user-memory)",
    )
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB)
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES_PER_FILE)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write L3 YOU.md (default: preview only)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-mine files even if ingest-index says unchanged",
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default="",
        help="Optional model-ledger.jsonl for soft tips",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    roots = [Path(p) for p in args.sessions_root] if args.sessions_root else None
    memory_root = Path(args.memory_root) if args.memory_root else None
    ledger = Path(args.ledger) if args.ledger else None

    result = mine(
        sessions_roots=roots,
        memory_root=memory_root,
        max_files=args.max_files,
        max_mb=args.max_mb,
        max_lines_per_file=args.max_lines,
        apply=args.apply,
        force=args.force,
        ledger_path=ledger,
    )
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result["message"])
        print(f"Preview: {result['preview_path']}")
        if result.get("applied_path"):
            print(f"Applied: {result['applied_path']}")
        else:
            print("Applied: (dry-run — pass --apply to write YOU.md)")
        for tip in result.get("tips") or []:
            print(
                f"  soft tip: {tip['task_type']} → {tip['model']} "
                f"n={tip['n']} conf={tip['confidence']}"
            )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
