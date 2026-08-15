#!/usr/bin/env python3
"""EFFICIENCY mode — cheap and fast ACC inject without dropping honesty.

Sources of truth (any one turns it ON):
  - env ACC_EFFICIENCY=1|true|yes
  - env ACC_LOAD_LEAN=1|true|yes  (legacy lean inject; unified here)
  - prefs lean=true or efficiency=true in preferences.json

Soft only: never forces host model picker APIs. Caps inject, skips Tier C
parade (host/loops/obs receipts), prefers shorter skill prompts.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

# Soft inject budgets (chars). Tier A always; B if room; C only when not lean.
DEFAULT_SOFT_CAP = 5500
EFFICIENCY_SOFT_CAP = 3200

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _env_map(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return environ if environ is not None else os.environ


def _truthy_env(name: str, environ: Mapping[str, str] | None = None) -> bool:
    raw = str(_env_map(environ).get(name, "") or "").strip().lower()
    return raw in _TRUTHY


def _truthy_pref(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)) and value == 1:
        return True
    if isinstance(value, str) and value.strip().lower() in _TRUTHY:
        return True
    return False


def is_on(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> bool:
    """True when ACC should run lean inject / efficiency caps."""
    if _truthy_env("ACC_EFFICIENCY", environ):
        return True
    if _truthy_env("ACC_LOAD_LEAN", environ):
        return True
    prefs = prefs or {}
    if _truthy_pref(prefs.get("lean")) or _truthy_pref(prefs.get("efficiency")):
        return True
    return False


def max_inject_chars(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> int:
    return EFFICIENCY_SOFT_CAP if is_on(prefs, environ=environ) else DEFAULT_SOFT_CAP


def skip_tier_c(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> bool:
    """Skip optional Tier C (host / loops / obs parade)."""
    return is_on(prefs, environ=environ)


def skip_verbose_receipts(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> bool:
    return is_on(prefs, environ=environ)


def prefer_short_skills(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> bool:
    return is_on(prefs, environ=environ)


def flags(
    prefs: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Stable flag dict for load_session / doctor / skills."""
    on = is_on(prefs, environ=environ)
    return {
        "efficiency": on,
        "load_lean": on,
        "max_inject_chars": EFFICIENCY_SOFT_CAP if on else DEFAULT_SOFT_CAP,
        "skip_tier_c": on,
        "skip_verbose_receipts": on,
        "prefer_short_skills": on,
        "sources": {
            "ACC_EFFICIENCY": _truthy_env("ACC_EFFICIENCY", environ),
            "ACC_LOAD_LEAN": _truthy_env("ACC_LOAD_LEAN", environ),
            "prefs_lean": _truthy_pref((prefs or {}).get("lean")),
            "prefs_efficiency": _truthy_pref((prefs or {}).get("efficiency")),
        },
    }


def inject_banner(flags_dict: Mapping[str, Any] | None = None) -> str:
    """One short line for SessionStart when efficiency is on."""
    f = dict(flags_dict or {})
    if not f.get("efficiency"):
        return ""
    return (
        "Efficiency: ON (lean inject). Cap inject. Skip host/loops/obs parade. "
        "Prefer short skill prompts. Model tips are soft only — ACC never forces "
        "host model picker."
    )


def main() -> int:
    """CLI: print flags JSON (and optional prefs from --project-root)."""
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="ACC efficiency / lean flags")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true", default=True)
    args = parser.parse_args()
    prefs: dict[str, Any] = {}
    root = Path(args.project_root).resolve()
    pref_path = root / ".codex" / "anyone-can-code" / "settings" / "preferences.json"
    if pref_path.exists():
        try:
            prefs = json.loads(pref_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prefs = {}
    print(json.dumps(flags(prefs), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
