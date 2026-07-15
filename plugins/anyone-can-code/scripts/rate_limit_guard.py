#!/usr/bin/env python3
"""Rate-limit + token-burn guard — CHEAP local reads of Codex session files.

Source of truth (observed in real Codex rollout JSONL, not a hook field in docs):
  event_msg → payload.type == "token_count"
  → rate_limits.primary.used_percent
  → rate_limits.secondary.used_percent
  → info.total_token_usage / last_token_usage

No invent: Codex hooks docs do NOT expose used_percent. We read disk like codeburn.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


RATE_WARN_PERCENT = 70
RATE_HARD_PERCENT = 90
# Fresh (non-cached) input tokens in one turn that mean "burning fast"
TOKEN_BURN_LAST_FRESH = 40_000
# Session cumulative total tokens that means "this chat is heavy"
TOKEN_BURN_SESSION_TOTAL = 2_000_000


def session_dirs() -> list[Path]:
    """Same idea as codeburn: CODEX_HOME/sessions then ~/.codex/sessions."""
    dirs: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        dirs.append(Path(codex_home) / "sessions")
    dirs.append(Path.home() / ".codex" / "sessions")
    # de-dupe while keeping order
    seen: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def list_recent_rollouts(roots: list[Path] | None = None, limit: int = 8) -> list[Path]:
    """Newest rollout-*.jsonl files under sessions trees."""
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
    return found[:limit]


def parse_token_count_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Extract rate + token burn numbers from one token_count payload."""
    if not isinstance(payload, dict) or payload.get("type") != "token_count":
        return None
    rate = payload.get("rate_limits") or {}
    if not isinstance(rate, dict):
        rate = {}
    primary = rate.get("primary") or {}
    secondary = rate.get("secondary") or {}
    info = payload.get("info") or {}
    total = (info.get("total_token_usage") or {}) if isinstance(info, dict) else {}
    last = (info.get("last_token_usage") or {}) if isinstance(info, dict) else {}

    def _pct(block: Any) -> float | None:
        if not isinstance(block, dict):
            return None
        raw = block.get("used_percent")
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def _int(block: Any, key: str) -> int:
        if not isinstance(block, dict):
            return 0
        try:
            return int(block.get(key) or 0)
        except (TypeError, ValueError):
            return 0

    last_input = _int(last, "input_tokens")
    last_cached = _int(last, "cached_input_tokens")
    last_fresh = max(0, last_input - last_cached) if last_cached else last_input

    return {
        "primary_used_percent": _pct(primary),
        "secondary_used_percent": _pct(secondary),
        "session_total_tokens": _int(total, "total_tokens"),
        "last_total_tokens": _int(last, "total_tokens"),
        "last_fresh_input_tokens": last_fresh,
        "last_cached_input_tokens": last_cached,
        "plan_type": rate.get("plan_type"),
        "rate_limit_reached_type": rate.get("rate_limit_reached_type"),
    }


def read_latest_snapshot(
    roots: list[Path] | None = None,
    *,
    max_files: int = 6,
    max_lines_per_file: int = 4000,
) -> dict[str, Any]:
    """Walk newest rollouts; return last token_count snapshot found (or empty)."""
    for path in list_recent_rollouts(roots, limit=max_files):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        # Prefer end of file — rate limits update continuously
        for line in reversed(lines[-max_lines_per_file:]):
            line = line.strip()
            if not line or "token_count" not in line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "event_msg":
                continue
            snap = parse_token_count_payload(entry.get("payload") or {})
            if snap and (
                snap.get("primary_used_percent") is not None
                or snap.get("session_total_tokens")
            ):
                snap["source_file"] = str(path)
                return snap
    return {
        "primary_used_percent": None,
        "secondary_used_percent": None,
        "session_total_tokens": 0,
        "last_total_tokens": 0,
        "last_fresh_input_tokens": 0,
        "last_cached_input_tokens": 0,
        "source_file": "",
        "unknown": True,
    }


def assess_rate_limit(
    primary_percent: float | int | None,
    secondary_percent: float | int | None = None,
) -> dict[str, Any]:
    """Hard warn at 70% and 90% on primary (or secondary if higher)."""
    candidates: list[float] = []
    for raw in (primary_percent, secondary_percent):
        if raw is None:
            continue
        try:
            candidates.append(float(raw))
        except (TypeError, ValueError):
            continue
    if not candidates:
        return {
            "level": "unknown",
            "percent": None,
            "warn_70": False,
            "hard_90": False,
            "message": "",
            "user_line": "",
        }
    percent = max(candidates)
    if percent >= RATE_HARD_PERCENT:
        msg = (
            f"Rate limit almost full ({percent:.0f}%). "
            "Stop heavy work now. Save state. Split to a new chat or wait for reset."
        )
        return {
            "level": "hard",
            "percent": percent,
            "warn_70": True,
            "hard_90": True,
            "message": msg,
            "user_line": msg,
        }
    if percent >= RATE_WARN_PERCENT:
        msg = (
            f"Rate limit high ({percent:.0f}%). "
            "Slow down. Prefer cheap steps. Avoid big subagents and high reasoning."
        )
        return {
            "level": "warn",
            "percent": percent,
            "warn_70": True,
            "hard_90": False,
            "message": msg,
            "user_line": msg,
        }
    return {
        "level": "ok",
        "percent": percent,
        "warn_70": False,
        "hard_90": False,
        "message": f"Rate limit ok ({percent:.0f}%).",
        "user_line": "",
    }


def assess_token_burn(
    *,
    session_total_tokens: int = 0,
    last_fresh_input_tokens: int = 0,
) -> dict[str, Any]:
    """Warn when this session is burning tokens fast. CHEAP local math."""
    reasons: list[str] = []
    if int(last_fresh_input_tokens or 0) >= TOKEN_BURN_LAST_FRESH:
        reasons.append(
            f"last turn used ~{int(last_fresh_input_tokens):,} fresh tokens"
        )
    if int(session_total_tokens or 0) >= TOKEN_BURN_SESSION_TOTAL:
        reasons.append(
            f"this chat total ~{int(session_total_tokens):,} tokens"
        )
    if not reasons:
        return {
            "burning": False,
            "message": "",
            "user_line": "",
            "session_total_tokens": int(session_total_tokens or 0),
            "last_fresh_input_tokens": int(last_fresh_input_tokens or 0),
        }
    msg = (
        "Token burn warning: "
        + "; ".join(reasons)
        + ". Prefer short context, fewer tools, lower reasoning."
    )
    return {
        "burning": True,
        "message": msg,
        "user_line": msg,
        "session_total_tokens": int(session_total_tokens or 0),
        "last_fresh_input_tokens": int(last_fresh_input_tokens or 0),
    }


def build_guard_lines(snapshot: dict[str, Any] | None = None) -> list[str]:
    """Plain lines to inject into session context. Empty when all quiet."""
    snap = snapshot if snapshot is not None else read_latest_snapshot()
    lines: list[str] = []
    rate = assess_rate_limit(
        snap.get("primary_used_percent"),
        snap.get("secondary_used_percent"),
    )
    if rate.get("user_line"):
        lines.append(f"RATE LIMIT: {rate['user_line']}")
    burn = assess_token_burn(
        session_total_tokens=int(snap.get("session_total_tokens") or 0),
        last_fresh_input_tokens=int(snap.get("last_fresh_input_tokens") or 0),
    )
    if burn.get("user_line"):
        lines.append(f"TOKEN BURN: {burn['user_line']}")
    return lines


def main() -> None:
    snap = read_latest_snapshot()
    rate = assess_rate_limit(
        snap.get("primary_used_percent"),
        snap.get("secondary_used_percent"),
    )
    burn = assess_token_burn(
        session_total_tokens=int(snap.get("session_total_tokens") or 0),
        last_fresh_input_tokens=int(snap.get("last_fresh_input_tokens") or 0),
    )
    print(
        json.dumps(
            {"snapshot": snap, "rate": rate, "burn": burn, "lines": build_guard_lines(snap)},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
