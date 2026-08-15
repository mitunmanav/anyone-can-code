#!/usr/bin/env python3
"""ACC approval grades — prefs + guard behavior hints.

Grades: off | ask | allowlist | strict

ACC layer only. Does **not** invent or set Codex host APIs
(--sandbox, --ask-for-approval, approval_policy, danger-full-access).
User still controls host via Codex /permissions and config.toml.

Research analogs (product UX, not APIs we call):
- Cursor run modes: allowlist / sandbox / auto-review
- Windsurf/Devin terminal auto-exec: Disabled / Allowlist Only / Auto / Turbo
- Codex: sandbox + approval policy (two layers; PermissionRequest hooks)

Used by $approval-mode skill and optional PermissionRequest audit path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

GRADES = ("off", "ask", "allowlist", "strict")
DEFAULT_GRADE = "ask"
PREF_KEY = "approval_mode"
ALLOWLIST_KEY = "approval_allowlist"

_ALIASES = {
    "off": "off",
    "none": "off",
    "disabled": "off",
    "ask": "ask",
    "default": "ask",
    "allowlist": "allowlist",
    "allow-list": "allowlist",
    "allow_list": "allowlist",
    "whitelist": "allowlist",
    "strict": "strict",
    "tight": "strict",
    "paranoid": "strict",
}

# Guard behavior flags per grade (ACC audit/guard only).
_HINTS: dict[str, dict[str, Any]] = {
    "off": {
        "layer_active": False,
        "auto_allow_safe_reads": False,
        "auto_allow_safe_bash": False,
        "use_user_allowlist": False,
        "force_prompt": True,
        "extra_caution": False,
        "user_line": (
            "ACC approval grade OFF. ACC will not auto-allow tools. "
            "Codex host prompts still apply. Use /permissions for host mode."
        ),
        "agent_line": (
            "approval_mode=off: do not ACC-auto-allow. Leave PermissionRequest "
            "to Codex. Still honor hard PreToolUse denials from guard."
        ),
    },
    "ask": {
        "layer_active": True,
        "auto_allow_safe_reads": True,
        "auto_allow_safe_bash": True,
        "use_user_allowlist": False,
        "force_prompt": False,
        "extra_caution": False,
        "user_line": (
            "ACC grade ASK (default). Safe reads + safe test/status shell may "
            "auto-allow. Risky steps still ask you. Codex sandbox stays on."
        ),
        "agent_line": (
            "approval_mode=ask: auto-allow only known-safe reads and safe bash "
            "prefixes (pytest/git status/…). Else normal Codex approval + plain hint."
        ),
    },
    "allowlist": {
        "layer_active": True,
        "auto_allow_safe_reads": True,
        "auto_allow_safe_bash": False,
        "use_user_allowlist": True,
        "force_prompt": False,
        "extra_caution": False,
        "user_line": (
            "ACC grade ALLOWLIST. Safe reads may auto-allow. Shell auto-allows "
            "only if it matches your approval_allowlist. Everything else asks."
        ),
        "agent_line": (
            "approval_mode=allowlist: auto-allow safe reads + bash matching "
            "prefs approval_allowlist prefixes only. No broad safe-bash set."
        ),
    },
    "strict": {
        "layer_active": True,
        "auto_allow_safe_reads": False,
        "auto_allow_safe_bash": False,
        "use_user_allowlist": False,
        "force_prompt": True,
        "extra_caution": True,
        "user_line": (
            "ACC grade STRICT. ACC never auto-allows. Every tool step may show "
            "a Codex approval prompt. Best for production-caution work."
        ),
        "agent_line": (
            "approval_mode=strict: never ACC-auto-allow. Always leave normal "
            "Codex prompt. Prefer short plain caution. Hard guard denials still block."
        ),
    },
}

CODEX_BOUNDARY = (
    "Codex owns real sandbox + approval policy "
    "(docs: agent-approvals-security, hooks PermissionRequest, /permissions). "
    "ACC grades only steer ACC hook soft auto-allow + plain hints. "
    "User sets host mode in Codex — ACC does not rewrite config.toml."
)


def normalize_grade(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "-")
    raw = raw.replace("_", "-") if raw not in _ALIASES else raw
    # try both underscore and hyphen forms
    key = str(value or "").strip().lower().replace(" ", "_")
    if key in _ALIASES:
        return _ALIASES[key]
    key2 = key.replace("_", "-")
    if key2 in _ALIASES:
        return _ALIASES[key2]
    key3 = key.replace("-", "_")
    if key3 in _ALIASES:
        return _ALIASES[key3]
    return DEFAULT_GRADE


def grade_from_prefs(prefs: dict[str, Any] | None) -> str:
    prefs = prefs or {}
    return normalize_grade(prefs.get(PREF_KEY))


def guard_hints(grade: str) -> dict[str, Any]:
    g = normalize_grade(grade)
    base = dict(_HINTS[g])
    base["grade"] = g
    return base


def describe_grade(grade: str) -> dict[str, Any]:
    h = guard_hints(grade)
    return {
        "grade": h["grade"],
        "user_line": h["user_line"],
        "agent_line": h["agent_line"],
        "codex_boundary": CODEX_BOUNDARY,
        "hints": {
            "layer_active": h["layer_active"],
            "auto_allow_safe_reads": h["auto_allow_safe_reads"],
            "auto_allow_safe_bash": h["auto_allow_safe_bash"],
            "use_user_allowlist": h["use_user_allowlist"],
            "force_prompt": h["force_prompt"],
            "extra_caution": h["extra_caution"],
        },
    }


def normalize_allowlist(items: Any) -> list[str]:
    if items is None:
        return []
    if isinstance(items, str):
        items = [items]
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out[:100]


def allowlist_from_prefs(prefs: dict[str, Any] | None) -> list[str]:
    prefs = prefs or {}
    return normalize_allowlist(prefs.get(ALLOWLIST_KEY))


def command_matches_allowlist(command: str, allowlist: list[str] | None) -> bool:
    cmd = str(command or "").strip().lower()
    if not cmd:
        return False
    for entry in allowlist or []:
        prefix = str(entry or "").strip().lower()
        if not prefix:
            continue
        if cmd == prefix or cmd.startswith(prefix + " ") or cmd.startswith(prefix + "\t"):
            return True
        # exact multi-word prefix without trailing space already handled;
        # also allow entry that is full command start without extra args requirement
        if cmd.startswith(prefix) and (
            len(cmd) == len(prefix) or cmd[len(prefix)] in " \t\n|"
        ):
            return True
    return False


def _bash_command(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        return str(tool_input.get("command") or "")
    if isinstance(tool_input, str):
        return tool_input
    return ""


def _is_bash_tool(tool_name: str) -> bool:
    name = str(tool_name or "")
    return name in {"Bash", "bash", "Shell", "shell"} or name.endswith("Bash")


def _is_read_tool(tool_name: str, is_safe_fn: Callable[..., bool] | None) -> bool:
    """True when tool is a safe read — prefer is_safe_fn for shared audit set."""
    name = str(tool_name or "")
    if is_safe_fn is not None:
        # Only count as "read" if safe_fn allows and it is not bash
        if _is_bash_tool(name):
            return False
        try:
            return bool(is_safe_fn(name, {}))
        except TypeError:
            return bool(is_safe_fn(name, None))
    # Fallback small set (mirrors audit SAFE_READ_TOOLS names)
    return any(
        token in name
        for token in (
            "Read",
            "Grep",
            "Glob",
            "LS",
            "Search",
            "WebSearch",
            "read_file",
            "list_dir",
            "grep",
        )
    )


def should_auto_allow(
    grade: str,
    tool_name: str,
    tool_input: Any,
    *,
    is_safe_fn: Callable[[str, Any], bool] | None = None,
    allowlist: list[str] | None = None,
) -> bool:
    """Whether ACC PermissionRequest should auto-allow this tool.

    is_safe_fn: typically audit.is_safe_auto_allow (reads + safe bash prefixes).
    """
    g = normalize_grade(grade)
    hints = guard_hints(g)

    if not hints["layer_active"] or hints["force_prompt"]:
        # off + strict: never ACC auto-allow
        if g in {"off", "strict"}:
            return False

    if g == "ask":
        if is_safe_fn is None:
            return False
        return bool(is_safe_fn(tool_name, tool_input))

    if g == "allowlist":
        # Safe reads always OK in allowlist mode
        if hints["auto_allow_safe_reads"] and _is_read_tool(tool_name, is_safe_fn):
            return True
        if _is_bash_tool(tool_name):
            cmd = _bash_command(tool_input)
            # Never auto-allow if base safety fails when fn provided
            if is_safe_fn is not None:
                # allowlist can allow commands beyond default safe bash set,
                # but still block if command is empty
                if not str(cmd).strip():
                    return False
            return command_matches_allowlist(cmd, allowlist or [])
        # Non-bash non-read (edit/patch/MCP): never ACC auto-allow
        return False

    return False


def set_grade(prefs: dict[str, Any], grade: str) -> dict[str, Any]:
    prefs = dict(prefs or {})
    prefs[PREF_KEY] = normalize_grade(grade)
    return prefs


def set_allowlist(prefs: dict[str, Any], items: Any) -> dict[str, Any]:
    prefs = dict(prefs or {})
    prefs[ALLOWLIST_KEY] = normalize_allowlist(items)
    return prefs


def apply_grade(
    repo_root: Path,
    grade: str,
    *,
    allowlist: list[str] | None = None,
) -> dict[str, Any]:
    """Write grade (+ optional allowlist) into project preferences.json."""
    hooks = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
    if str(hooks) not in sys.path:
        sys.path.insert(0, str(hooks))
    import state  # type: ignore

    updates: dict[str, Any] = {PREF_KEY: normalize_grade(grade)}
    if allowlist is not None:
        updates[ALLOWLIST_KEY] = normalize_allowlist(allowlist)
    return state.write_preferences(Path(repo_root), updates)


def snapshot(repo_root: Path | None = None) -> dict[str, Any]:
    prefs: dict[str, Any] = {}
    if repo_root is not None:
        hooks = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
        if str(hooks) not in sys.path:
            sys.path.insert(0, str(hooks))
        import state  # type: ignore

        prefs = state.read_preferences(Path(repo_root))
    grade = grade_from_prefs(prefs)
    desc = describe_grade(grade)
    return {
        "grade": grade,
        "grades": list(GRADES),
        "allowlist": allowlist_from_prefs(prefs),
        "user_line": desc["user_line"],
        "agent_line": desc["agent_line"],
        "codex_boundary": desc["codex_boundary"],
        "hints": desc["hints"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACC approval grades (off|ask|allowlist|strict). Prefs + guard hints only."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root with .codex/anyone-can-code/settings/",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON snapshot")
    parser.add_argument(
        "--set",
        dest="set_grade",
        metavar="GRADE",
        help="Write approval_mode grade into preferences",
    )
    parser.add_argument(
        "--allowlist",
        nargs="*",
        default=None,
        help="With --set allowlist: replace approval_allowlist entries",
    )
    parser.add_argument(
        "--describe",
        metavar="GRADE",
        help="Describe one grade without reading disk",
    )
    args = parser.parse_args(argv)

    if args.describe:
        print(json.dumps(describe_grade(args.describe), indent=2))
        return 0

    root = Path(args.project_root).resolve()
    if args.set_grade:
        allow = args.allowlist
        # Only pass allowlist when user provided the flag path for allowlist grade
        if allow is None and normalize_grade(args.set_grade) == "allowlist":
            allow = None  # keep existing
        out = apply_grade(root, args.set_grade, allowlist=allow)
        if args.json:
            print(
                json.dumps(
                    {
                        "written": True,
                        "grade": out.get(PREF_KEY),
                        "allowlist": out.get(ALLOWLIST_KEY, []),
                        **describe_grade(out.get(PREF_KEY)),
                    },
                    indent=2,
                )
            )
        else:
            d = describe_grade(out.get(PREF_KEY))
            print(f"grade={d['grade']}")
            print(d["user_line"])
        return 0

    snap = snapshot(root)
    if args.json:
        print(json.dumps(snap, indent=2))
    else:
        print(f"grade={snap['grade']}")
        print(snap["user_line"])
        if snap["allowlist"]:
            print("allowlist: " + ", ".join(snap["allowlist"]))
        print(snap["codex_boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
