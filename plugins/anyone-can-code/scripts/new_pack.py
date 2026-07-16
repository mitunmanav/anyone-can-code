#!/usr/bin/env python3
"""NEW items 36–47: modes, teach, story log, secret/sniff, profile, plan lock, install.

Cheap local only. Explain → user decides. No ACC self-audit (removed).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import cost_labels
except Exception:  # pragma: no cover
    cost_labels = None  # type: ignore

try:
    import safety_receipts
except Exception:  # pragma: no cover
    safety_receipts = None  # type: ignore


def _tag(kind: str, text: str) -> str:
    if cost_labels is not None:
        return cost_labels.tag_line(text, kind)
    return f"[{'CHEAP' if kind == 'cheap' else 'HUNGRY'}] {text}"


# --- 36: three modes + 4 knobs ---
# Aliases: non-tech≈builder, middle≈mixed, developer≈developer

MODE_ALIASES = {
    "non-tech": "non-tech",
    "nontech": "non-tech",
    "builder": "non-tech",
    "beginner": "non-tech",
    "middle": "middle",
    "mixed": "middle",
    "intermediate": "middle",
    "developer": "developer",
    "dev": "developer",
    "expert": "developer",
}

# knobs: plain (0-3), teach (0-3), tech_shown (0-3), questions ("life"|"mixed"|"tech")
MODE_KNOBS: dict[str, dict[str, Any]] = {
    "non-tech": {
        "plain": 3,
        "teach": 3,
        "tech_shown": 0,
        "questions": "life",
        "persona": "builder",
    },
    "middle": {
        "plain": 2,
        "teach": 1,
        "tech_shown": 1,
        "questions": "mixed",
        "persona": "mixed",
    },
    "developer": {
        "plain": 1,
        "teach": 0,
        "tech_shown": 3,
        "questions": "tech",
        "persona": "developer",
    },
}


def normalize_mode(mode: str | None) -> str:
    key = str(mode or "middle").strip().lower()
    return MODE_ALIASES.get(key, "middle")


def mode_knobs(mode: str | None) -> dict[str, Any]:
    m = normalize_mode(mode)
    knobs = dict(MODE_KNOBS[m])
    knobs["mode"] = m
    knobs["cost"] = "cheap"
    knobs["user_line"] = _tag(
        "cheap",
        f"Mode {m}: plain={knobs['plain']}/3 teach={knobs['teach']}/3 "
        f"tech={knobs['tech_shown']}/3 questions={knobs['questions']}. You can change anytime.",
    )
    return knobs


# --- 37: teach layer ---

_TEACH_BANK = {
    "plan": "A plan is a short list of steps before we touch files.",
    "verify": "Verify means we prove it works — run a check, not just hope.",
    "commit": "A commit is a save-point for your project history.",
    "deploy": "Deploy means put the app where people can use it for real.",
    "secret": "Secrets are passwords and keys. Never put them in chat or code you share.",
    "test": "A test is a small check the computer runs to catch breaks early.",
}


def teach_line(topic: str, mode: str | None) -> str:
    knobs = mode_knobs(mode)
    if int(knobs["teach"]) <= 0:
        return ""
    key = str(topic or "").strip().lower()
    base = _TEACH_BANK.get(key) or f"Short note: {key or 'this step'} matters for a safe build."
    if knobs["teach"] >= 3:
        return f"Teach: {base}"
    if knobs["teach"] == 1:
        return f"Tip: {base}"
    return f"Teach: {base}"


def teach_for_request(request: str, mode: str | None) -> list[str]:
    knobs = mode_knobs(mode)
    if knobs["teach"] <= 0:
        return []
    low = (request or "").lower()
    out: list[str] = []
    for topic in _TEACH_BANK:
        if topic in low:
            line = teach_line(topic, mode)
            if line:
                out.append(line)
    if not out and knobs["teach"] >= 2:
        out.append(teach_line("plan", mode))
    return out


# --- 38: Story Log (plain-life) ---

def story_from_receipt(receipt: dict[str, Any] | str) -> dict[str, Any]:
    """Split tech (quiet) vs life (ask human words)."""
    if isinstance(receipt, str):
        text = receipt
        data: dict[str, Any] = {"raw": receipt}
    else:
        data = dict(receipt or {})
        text = json.dumps(data, ensure_ascii=True)

    # life pile: what a human cares about
    action = str(data.get("action") or data.get("type") or data.get("event") or "work")
    status = str(data.get("status") or data.get("result") or "").lower()
    if "fail" in status or "block" in status:
        life = f"We hit a wall on {action}. Need your choice before more risk."
    elif "approve" in status or "ok" in status or "pass" in status:
        life = f"Safe step done for {action}."
    else:
        life = f"Working on {action}."

    tech_quiet = True  # agent handles tech pile silently
    return {
        "life": life,
        "tech_quiet": tech_quiet,
        "ask_user": "fail" in status or "block" in status or data.get("needs_user"),
        "approval_plain": plain_approval_box(data),
        "user_line": life,
    }


def plain_approval_box(action: dict[str, Any] | None = None) -> str:
    """Translate Codex-style approval ask into plain life words."""
    action = action or {}
    kind = str(action.get("type") or action.get("action") or "this step")
    return (
        f"Codex wants a yes/no for: {kind}. "
        "In plain words: allow this change, or say no and we stop."
    )


def story_log_from_dir(repo_root: Path, limit: int = 5) -> list[dict[str, Any]]:
    if safety_receipts is None:
        return []
    root = Path(repo_root)
    rdir = safety_receipts.receipts_dir(root)
    if not rdir.is_dir():
        return []
    files = sorted(rdir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    stories: list[dict[str, Any]] = []
    for path in files[: max(1, limit)]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {"raw": path.name, "type": "receipt"}
        stories.append(story_from_receipt(data))
    return stories


# --- 39: secret guard ---

_SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"), "api/key/token assignment"),
    (re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{4,}['\"]"), "password assignment"),
    (re.compile(r"(?i)-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"(?i)\b(sk|pk|rk)-[A-Za-z0-9]{16,}\b"), "long secret-looking token"),
    (re.compile(r"(?i)AWS[A-Z0-9]{16,}"), "aws-style key"),
]


def scan_secrets(text: str) -> dict[str, Any]:
    hits: list[str] = []
    body = text or ""
    for pattern, label in _SECRET_PATTERNS:
        if pattern.search(body):
            hits.append(label)
    ok = not hits
    return {
        "ok": ok,
        "hits": hits,
        "user_line": (
            "No secret-looking text found."
            if ok
            else "Stop — possible secret found: " + "; ".join(hits) + ". Do not save or share."
        ),
        "force": False,
        "cost": "cheap",
    }


# --- 40: bad-code sniff ---

_BAD_CODE = [
    (re.compile(r"\brm\s+-rf\s+/\b"), "wipe whole disk command"),
    (re.compile(r"\bDROP\s+TABLE\b", re.I), "drop table"),
    (re.compile(r"\beval\s*\("), "eval()"),
    (re.compile(r"\bexec\s*\(\s*['\"]"), "exec of string"),
    (re.compile(r"\bsubprocess\.[a-z]+\([^)]*shell\s*=\s*True", re.I), "shell=True subprocess"),
    (re.compile(r"(?i)ALLOW_PUBLIC_REGISTRATION\s*=\s*[\"']?true"), "open signup flag"),
    (re.compile(r"(?i)DEFAULT_ADMIN_PASSWORD\s*="), "default admin password"),
    (re.compile(r":\s*['\"]admin123['\"]"), "admin123 password"),
]


def sniff_code(text: str) -> dict[str, Any]:
    hits: list[str] = []
    body = text or ""
    for pattern, label in _BAD_CODE:
        if pattern.search(body):
            hits.append(label)
    ok = not hits
    return {
        "ok": ok,
        "hits": hits,
        "user_line": (
            "Code smell check: no obvious danger."
            if ok
            else "Danger smell: " + "; ".join(hits) + ". Fix or explain before run."
        ),
        "force": False,
        "cost": "cheap",
    }


# --- 41: passive user profile ---

def update_passive_profile(
    prefs: dict[str, Any],
    *,
    signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Quietly merge chat signals into prefs.passive_profile. Never overwrites explicit about_you."""
    prefs = dict(prefs or {})
    profile = dict(prefs.get("passive_profile") or {})
    signals = signals or {}
    for key in ("skill_hint", "pace", "likes_short", "asks_life", "asks_tech"):
        if key in signals and signals[key] not in (None, ""):
            profile[key] = signals[key]
    # derive from message length / words if provided
    msg = str(signals.get("last_user_message") or "")
    if msg:
        if len(msg.split()) <= 8:
            profile["likes_short"] = True
        if any(w in msg.lower() for w in ("why", "what is", "explain", "teach")):
            profile["wants_teach"] = True
        if any(w in msg.lower() for w in ("api", "refactor", "typescript", "sql")):
            profile["asks_tech"] = True
    prefs["passive_profile"] = profile
    return prefs


def passive_profile_line(prefs: dict[str, Any] | None) -> str:
    profile = (prefs or {}).get("passive_profile") or {}
    if not profile:
        return ""
    bits = [f"{k}={v}" for k, v in sorted(profile.items())][:6]
    return f"Passive profile (quiet): {', '.join(bits)}."[:240]


# --- 42: personal vocabulary ---

def vocab_list(prefs: dict[str, Any] | None) -> list[str]:
    raw = (prefs or {}).get("vocabulary") or (prefs or {}).get("personal_vocabulary") or []
    if isinstance(raw, str):
        return [w.strip() for w in raw.split(",") if w.strip()]
    if isinstance(raw, list):
        return [str(w).strip() for w in raw if str(w).strip()]
    return []


def add_vocab(prefs: dict[str, Any], words: list[str]) -> dict[str, Any]:
    prefs = dict(prefs or {})
    current = vocab_list(prefs)
    for w in words:
        w = str(w).strip()
        if w and w not in current:
            current.append(w)
    prefs["vocabulary"] = current[:100]
    return prefs


def apply_vocab(text: str, prefs: dict[str, Any] | None) -> str:
    """Replace known tech words with user's plain synonyms if stored as 'tech=plain'."""
    result = text or ""
    for item in vocab_list(prefs):
        if "=" in item:
            tech, plain = item.split("=", 1)
            tech, plain = tech.strip(), plain.strip()
            if tech and plain:
                result = re.sub(re.escape(tech), plain, result, flags=re.I)
    return result


# --- 43: contradiction guard ---

def find_contradictions(
    decisions: list[str] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Flag simple opposing decisions (A vs not A / choose X vs choose Y)."""
    lines: list[str] = []
    for d in decisions or []:
        if isinstance(d, dict):
            lines.append(str(d.get("text") or d.get("decision") or d))
        else:
            lines.append(str(d))
    lows = [ln.strip().lower() for ln in lines if ln.strip()]
    pairs: list[str] = []
    # naive: "use X" vs "do not use X" / "no X"
    for i, a in enumerate(lows):
        for b in lows[i + 1 :]:
            if a == b:
                continue
            # strip common prefixes
            aa = re.sub(r"^(use|choose|pick|go with)\s+", "", a)
            bb = re.sub(r"^(use|choose|pick|go with)\s+", "", b)
            if aa.startswith("no ") and aa[3:] == bb:
                pairs.append(f"'{lines[i]}' vs '{lines[lows.index(b)] if b in lows else b}'")
            elif bb.startswith("no ") and bb[3:] == aa:
                pairs.append(f"'{lines[i]}' vs conflict")
            elif (" not " in a or a.startswith("don't") or a.startswith("do not")) and any(
                tok in b for tok in a.replace("don't", "").replace("do not", "").split() if len(tok) > 3
            ):
                # weak signal
                if any(t in b for t in ("use", "yes", "always")) and any(
                    t in a for t in ("not", "never", "don't")
                ):
                    pairs.append(f"possible conflict: '{lines[i][:60]}' / '{b[:60]}'")
    # also exact opposites: "sqlite" vs "postgres" when both chosen
    stacks = []
    for ln in lows:
        for db in ("sqlite", "postgres", "mysql", "mongodb"):
            if db in ln and ("use" in ln or "choose" in ln or "with" in ln):
                stacks.append(db)
    if len(set(stacks)) > 1:
        pairs.append("database choices conflict: " + ", ".join(sorted(set(stacks))))

    ok = not pairs
    return {
        "ok": ok,
        "conflicts": pairs,
        "user_line": (
            "No clear contradiction in decisions."
            if ok
            else "Hold on — decisions disagree: " + "; ".join(pairs[:3]) + ". Pick one."
        ),
        "force": False,
    }


# --- 44: adaptive plan-lock ---

def plan_lock_state(
    *,
    plan_approved: bool,
    user_requests_change: bool,
    locked: bool = False,
) -> dict[str, Any]:
    if user_requests_change:
        return {
            "locked": False,
            "action": "unlock",
            "user_line": "Plan unlocked because you asked to change it.",
        }
    if plan_approved or locked:
        return {
            "locked": True,
            "action": "lock",
            "user_line": "Plan locked. We follow it until you say change.",
        }
    return {
        "locked": False,
        "action": "open",
        "user_line": "Plan still open. Approve to lock.",
    }


# --- 46: automations opt-in ---

def automation_setup_prompt(prefs: dict[str, Any] | None = None) -> dict[str, Any]:
    prefs = prefs or {}
    enabled = bool(prefs.get("automations_opt_in"))
    return {
        "id": "automations_opt_in",
        "enabled": enabled,
        "default": False,
        "user_line": _tag(
            "hungry",
            "Set up automations (background scheduled jobs)? They use tokens. "
            "Say YES to set up, or NO to skip. Nothing turns on alone.",
        ),
        "agent_line": (
            "Automations off until user says yes at setup. "
            "After real use, suggest only automations that match observed needs."
        ),
        "adaptive_hint": (
            "After a few sessions, suggest only: recap if they leave mid-task; "
            "stuck nudge if idle days; skip the rest."
        ),
    }


def set_automations_opt_in(prefs: dict[str, Any], yes: bool) -> dict[str, Any]:
    prefs = dict(prefs or {})
    prefs["automations_opt_in"] = bool(yes)
    if not yes:
        prefs["automation_preference"] = "off"
    return prefs


# --- 47: install marketplace URL ---

def install_howto() -> dict[str, Any]:
    return {
        "id": "marketplace_install",
        "native": "Codex plugin marketplace + trust + restart + $setup",
        "cost": "cheap",
        "user_line": _tag(
            "cheap",
            "Install like the Codex app: paste the marketplace URL into Codex Plugins, "
            "trust the plugin when asked, restart Codex, then run $setup. You choose.",
        ),
        "setup_steps": [
            "Open Codex → Plugins / Marketplace",
            "Paste the ACC marketplace URL (from the project README)",
            "Trust / install Anyone Can Code when prompted",
            "Restart Codex if asked",
            "Open your project and run $setup",
            "Answer first-run: builder / developer / mixed (or non-tech / middle / developer)",
        ],
        "agent_line": (
            "Do not invent installers. Guide marketplace URL paste + trust hooks + restart + $setup."
        ),
    }


# --- menu ---

def all_features() -> list[dict[str, Any]]:
    return [
        {"id": "modes", "user_line": mode_knobs("middle")["user_line"]},
        {"id": "teach", "user_line": _tag("cheap", "Teach layer follows mode (off for developer).")},
        {"id": "story_log", "user_line": _tag("cheap", "Safety receipts become plain-life story lines.")},
        {"id": "secret_guard", "user_line": _tag("cheap", "Scan for secrets before save/share.")},
        {"id": "bad_code_sniff", "user_line": _tag("cheap", "Smell dangerous code before it runs.")},
        {"id": "passive_profile", "user_line": _tag("cheap", "Quiet profile from how you chat.")},
        {"id": "vocabulary", "user_line": _tag("cheap", "Your personal plain-word list.")},
        {"id": "contradiction", "user_line": _tag("cheap", "Catch decisions that disagree.")},
        {"id": "plan_lock", "user_line": _tag("cheap", "Lock plan after approve; unlock if you change.")},
        {"id": "automations_opt_in", "user_line": automation_setup_prompt()["user_line"]},
        {"id": "marketplace_install", "user_line": install_howto()["user_line"]},
    ]


def plain_menu() -> str:
    lines = ["New tools (cheap, you choose):"]
    for f in all_features():
        lines.append(f"- {f['id']}: {f['user_line']}")
    lines.append("Nothing forced.")
    return "\n".join(lines)
