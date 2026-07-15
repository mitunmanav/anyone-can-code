#!/usr/bin/env python3
"""Phase F — expand: CLI host, other agents later, ACC audits ACC.

Wrap native Codex plugin model. No fake Claude/Cursor ports.
Explain → suggest → user decides. [CHEAP]/[HUNGRY].
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cost_labels
except Exception:  # pragma: no cover
    cost_labels = None  # type: ignore

try:
    import doctor as _doctor
except Exception:  # pragma: no cover
    _doctor = None  # type: ignore

SKILL_BUDGET = 4000


def _tag(kind: str, text: str) -> str:
    if cost_labels is not None:
        return cost_labels.tag_line(text, kind)
    tag = "[CHEAP]" if kind == "cheap" else "[HUNGRY]"
    return f"{tag} {text}"


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


# --- 33: Codex CLI port (same plugin bundle) ---

def detect_host(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Which Codex surface is running. Same plugin; different shell."""
    context = context or {}
    surface = _norm(context.get("surface") or context.get("host") or context.get("app"))
    if surface in {"cli", "terminal", "tui"}:
        hid = "cli"
    elif surface in {"exec", "headless", "noninteractive", "ci"}:
        hid = "exec"
    elif surface in {"desktop", "app", "windows app", "chatgpt desktop"}:
        hid = "desktop"
    elif surface in {"ide", "vscode", "extension"}:
        hid = "ide"
    else:
        # default: treat as desktop-friendly unless env says CI/exec
        import os

        if os.environ.get("CI") or os.environ.get("CODEX_CI"):
            hid = "exec"
        else:
            hid = "desktop"

    lines = {
        "desktop": "Host: Codex Desktop. Full UI (review pane, Sites, notifications).",
        "cli": "Host: Codex CLI. Same plugin skills/hooks. Use terminal commands and /slash.",
        "exec": "Host: codex exec (headless). Scripts/CI. Default sandbox read-only.",
        "ide": "Host: Codex IDE extension. Same plugin model; editor-first.",
    }
    return {
        "id": hid,
        "supports_plugins": True,
        "user_line": lines.get(hid, lines["desktop"]),
        "agent_line": (
            "One ACC plugin bundle for Desktop + CLI + IDE. "
            "Do not rebuild per host. Adapt UI words to the host."
        ),
    }


def cli_howto() -> dict[str, Any]:
    return {
        "id": "cli_port",
        "native": "Codex CLI plugin directory (same plugin.json bundle)",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Want ACC in the terminal? Install the same Anyone Can Code plugin in Codex CLI. "
            "Same plan → build → verify. No second product. You choose Desktop or CLI.",
        ),
        "agent_line": (
            "CLI port = same plugin. Guide install from marketplace or local path. "
            "Hooks/skills/MCP work when CLI supports plugins. Prefer python3 scripts."
        ),
        "setup_steps": [
            "Install Codex CLI and sign in",
            "Add ACC marketplace or install local plugin folder (same .codex-plugin/plugin.json)",
            "Open a project folder in the terminal",
            "Run codex, then use ACC skills ($setup, plan, build, verify)",
            "Doctor: python plugins/anyone-can-code/scripts/doctor.py",
        ],
    }


# --- 34: other agents — honest later ---

def other_agents_howto() -> dict[str, Any]:
    return {
        "id": "other_agents",
        "native": "None yet (Codex-first)",
        "cost": "cheap",
        "status": "later",
        "force": False,
        "user_line": _tag(
            "cheap",
            "Claude, Cursor, and other agents: not yet. Codex first (Desktop + CLI). "
            "If you switch tools, say handoff so context can travel. Nothing forced.",
        ),
        "agent_line": (
            "Do not claim ACC runs on Claude/Cursor today. "
            "Other-agent ports are later. Offer handoff/export of state if user leaves Codex."
        ),
    }


# --- 35: ACC audits ACC ---

def _check(
    check_id: str,
    status: str,
    detail: str,
) -> dict[str, Any]:
    return {"id": check_id, "status": status, "detail": detail}


def self_audit(plugin_root: Path | None = None) -> dict[str, Any]:
    """Run cheap local checks on the ACC plugin itself. Plain report."""
    root = Path(plugin_root) if plugin_root is not None else PLUGIN_ROOT
    checks: list[dict[str, Any]] = []

    # Manifest
    manifest = root / ".codex-plugin" / "plugin.json"
    if not manifest.is_file():
        checks.append(_check("plugin_manifest", "fail", "Missing .codex-plugin/plugin.json"))
    else:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            missing = [k for k in ("name", "version", "skills") if k not in data]
            if missing:
                checks.append(
                    _check("plugin_manifest", "fail", f"Manifest missing fields: {', '.join(missing)}")
                )
            else:
                checks.append(
                    _check(
                        "plugin_manifest",
                        "pass",
                        f"{data.get('name')} v{data.get('version')}",
                    )
                )
        except (OSError, json.JSONDecodeError) as exc:
            checks.append(_check("plugin_manifest", "fail", f"Bad plugin.json: {exc}"))

    # Skill budget
    skills_root = root / "skills"
    if not skills_root.is_dir():
        checks.append(_check("skill_budget", "fail", "No skills/ folder"))
    else:
        over: list[str] = []
        count = 0
        for skill_md in sorted(skills_root.glob("*/SKILL.md")):
            count += 1
            try:
                size = len(skill_md.read_text(encoding="utf-8"))
            except OSError:
                continue
            if size > SKILL_BUDGET:
                over.append(f"{skill_md.parent.name}:{size}")
        if over:
            checks.append(
                _check("skill_budget", "fail", f"Over {SKILL_BUDGET} chars: {'; '.join(over)}")
            )
        else:
            checks.append(
                _check("skill_budget", "pass", f"{count} skills within {SKILL_BUDGET} chars")
            )

    # Hooks present
    hooks = root / "hooks" / "hooks.json"
    if hooks.is_file():
        try:
            json.loads(hooks.read_text(encoding="utf-8"))
            checks.append(_check("hooks", "pass", "hooks.json valid JSON"))
        except (OSError, json.JSONDecodeError) as exc:
            checks.append(_check("hooks", "fail", f"hooks.json bad: {exc}"))
    else:
        checks.append(_check("hooks", "fail", "Missing hooks/hooks.json"))

    # Doctor summary (best effort; may need project cwd)
    if _doctor is not None:
        try:
            d = _doctor.Doctor(json_mode=True)
            # Only plugin-local cheap checks when no project
            d.run_python()
            d.run_manifest() if hasattr(d, "run_manifest") else None
            # Prefer skill budget helper already defined
            budget = _doctor.run_skill_budget(skills_root)
            fail_b = [r for r in budget if r.get("status") == "FAIL"]
            if fail_b:
                checks.append(
                    _check(
                        "doctor_skills",
                        "fail",
                        "; ".join(r.get("detail", "") for r in fail_b[:5]),
                    )
                )
            else:
                checks.append(
                    _check("doctor_skills", "pass", f"doctor skill budget ok ({len(budget)})")
                )
        except Exception as exc:  # never block self-audit
            checks.append(_check("doctor_skills", "warn", f"doctor skip: {exc}"))
    else:
        checks.append(_check("doctor_skills", "warn", "doctor module unavailable"))

    # Proof rule present (orchestrator/verify)
    proof_ok = False
    for name in ("verify", "orchestrator"):
        path = skills_root / name / "SKILL.md"
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8").lower()
            except OSError:
                continue
            if "proof" in text or "verified" in text:
                proof_ok = True
                break
    checks.append(
        _check(
            "proof_rule",
            "pass" if proof_ok else "fail",
            "verify/orchestrator mention proof" if proof_ok else "missing proof language in skills",
        )
    )

    summary = {"pass": 0, "warn": 0, "fail": 0}
    for c in checks:
        st = c["status"]
        if st == "pass":
            summary["pass"] += 1
        elif st == "warn":
            summary["warn"] += 1
        else:
            summary["fail"] += 1

    ok = summary["fail"] == 0
    if ok:
        user_line = (
            f"ACC self-check: healthy. "
            f"{summary['pass']} pass, {summary['warn']} warn, {summary['fail']} fail. "
            "Plugin looks ready."
        )
    else:
        fails = [c["detail"] for c in checks if c["status"] == "fail"]
        user_line = (
            f"ACC self-check: problems found. "
            f"{summary['pass']} pass, {summary['warn']} warn, {summary['fail']} fail. "
            + " | ".join(fails[:3])
        )

    return {
        "id": "acc_audits_acc",
        "ok": ok,
        "summary": summary,
        "checks": checks,
        "plugin_root": str(root),
        "user_line": user_line,
        "agent_line": (
            "ACC audits ACC: run self_audit / expand_pack self-audit. "
            "Show plain pass/fail. Never claim healthy with fail>0. Doctor + proof rules."
        ),
        "cost": "cheap",
        "force": False,
    }


def self_audit_howto() -> dict[str, Any]:
    return {
        "id": "acc_audits_acc",
        "native": "ACC doctor + self_audit scripts",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Want ACC to check itself? Run self-audit (doctor + skill size + hooks + proof rules). "
            "You get a plain pass/fail list. Free. You choose when.",
        ),
        "agent_line": self_audit()["agent_line"],
    }


def all_features() -> list[dict[str, Any]]:
    return [cli_howto(), other_agents_howto(), self_audit_howto()]


def plain_menu() -> str:
    lines = ["Expand tools (Codex first). You choose:"]
    for f in all_features():
        lines.append(f"- {f['id']}: {f['user_line']}")
    lines.append("Other agents = later. Self-audit anytime. Nothing forced.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="ACC Phase F expand helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("self-audit", help="ACC audits ACC (plain health report)")
    p_audit.add_argument("--plugin-root", default=str(PLUGIN_ROOT))
    p_audit.add_argument("--json", action="store_true")

    p_host = sub.add_parser("host", help="Detect Codex host surface")
    p_host.add_argument("--surface", default="")
    p_host.add_argument("--json", action="store_true")

    p_menu = sub.add_parser("menu", help="Plain expand menu")
    p_menu.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.cmd == "self-audit":
        report = self_audit(Path(args.plugin_root))
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(report["user_line"])
            for c in report["checks"]:
                print(f"  [{c['status'].upper()}] {c['id']}: {c['detail']}")
        sys.exit(0 if report["ok"] else 1)
    if args.cmd == "host":
        h = detect_host({"surface": args.surface} if args.surface else None)
        if args.json:
            print(json.dumps(h, indent=2))
        else:
            print(h["user_line"])
        return
    if args.cmd == "menu":
        if args.json:
            print(json.dumps(all_features(), indent=2))
        else:
            print(plain_menu())


if __name__ == "__main__":
    main()
