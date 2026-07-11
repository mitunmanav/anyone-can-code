#!/usr/bin/env python3
"""
codeburn.py — Codex token usage analyzer for Anyone Can Code plugin.

Usage:
    python codeburn.py status          # compact one-liner
    python codeburn.py today           # today's usage breakdown
    python codeburn.py week            # last 7 days
    python codeburn.py report          # full report (7 day default)
    python codeburn.py report -p 30d   # 30 day window
    python codeburn.py report -p all   # entire history
    python codeburn.py report --format json
    python codeburn.py daemon          # start web dashboard
    python codeburn.py stop            # stop web daemon
    python codeburn.py export          # JSON export (7 days)
    python codeburn.py export -f csv   # CSV export
    python codeburn.py export -p all   # full history

Reads Codex session transcripts from ~/.codex/sessions/.
No API calls, no tokens spent on analysis. Pure disk reads.
"""

import argparse
import collections
import csv
import http.server
import io
import json
import os
import re
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, date
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── Tool name normalization ─────────────────────────────────────────────
TOOL_ALIASES = {
    "exec_command": "Bash",
    "read_file": "Read",
    "write_file": "Edit",
    "apply_diff": "Edit",
    "apply_patch": "Edit",
    "spawn_agent": "Agent",
    "dispatch_agent": "Agent",
    "grep_search": "Grep",
    "glob": "Grep",
    "web_search": "WebSearch",
    "read": "Read",
    "edit": "Edit",
    "bash": "Bash",
    "write": "Edit",
    "grep": "Grep",
    "shell": "Bash",
    "run": "Bash",
}

# MCP tool name normalization (server:tool -> standard name)
MCP_TOOL_ALIASES = {
    "read_multiple_files": "Read",
    "read_file": "Read",
    "read": "Read",
    "cat": "Read",
    "list_directory": "Read",
    "directory_tree": "Read",
    "ls": "Read",
    "write_file": "Edit",
    "write": "Edit",
    "edit_file": "Edit",
    "edit": "Edit",
    "apply_diff": "Edit",
    "apply_patch": "Edit",
    "create_directory": "Edit",
    "mkdir": "Edit",
    "move_file": "Bash",
    "mv": "Bash",
    "rm": "Bash",
    "copy_file": "Bash",
    "cp": "Bash",
    "exec_command": "Bash",
    "bash": "Bash",
    "shell": "Bash",
    "command": "Bash",
    "run_command": "Bash",
    "search_files": "Grep",
    "grep_search": "Grep",
    "grep": "Grep",
    "glob": "Grep",
    "find": "Grep",
    "web_search": "WebSearch",
    "search_web": "WebSearch",
    "spawn_agent": "Agent",
    "dispatch_agent": "Agent",
    "agent": "Agent",
    "read_text_file": "Read",
    "read_multiple_files": "Read",
    "list_allowed_directories": "Read",
    "list_directory": "Read",
    "list_mcp_resources": "Read",
    "list_mcp_resource_templates": "Read",
    "get_file_info": "Read",
    "mcp_search": "Grep",
    "search": "Grep",
    "js": "Bash",
    "node": "Bash",
}

# ── Activity classification patterns ─────────────────────────────────────
ACTIVITY_KEYWORDS = {
    "Debugging": ["fix", "error", "bug", "debug", "broken", "crash", "issue", "not working"],
    "Feature Dev": ["add", "create", "implement", "feature", "new", "build"],
    "Refactoring": ["refactor", "rename", "simplify", "extract", "clean", "restructure"],
    "Testing": ["pytest", "jest", "vitest", "test", "unittest", "spec"],
    "Git Ops": ["git commit", "git push", "git merge", "git rebase", "git pull"],
    "Build/Deploy": ["npm build", "docker", "deploy", "pm2", "pip install", "npm install", "yarn"],
    "Planning": ["plan", "spec", "design", "architecture", "clarify", "roadmap"],
    "Review": ["review", "audit", "verify", "check", "inspect"],
    "Brainstorming": ["brainstorm", "idea", "what if", "proposal", "suggest"],
    "Conversation": [],
}

# ── Constants ────────────────────────────────────────────────────────────
HTML_PATH = Path(__file__).parent / "codeburn.html"
SESSION_DIRS = []
PID_FILE = None
HTML_INLINE = ""

# ── Session discovery ────────────────────────────────────────────────────

def find_session_dirs():
    """Return list of session dirs to scan. Respects CODEX_HOME env var."""
    global SESSION_DIRS
    if SESSION_DIRS:
        return SESSION_DIRS

    dirs = []

    # 1. CODEX_HOME env var
    codex_home = os.environ.get("CODEX_HOME", "")
    if codex_home:
        dirs.append(Path(codex_home) / "sessions")

    # 2. WSL/Linux home
    dirs.append(Path.home() / ".codex" / "sessions")

    # 3. Windows home (when running in WSL)
    if sys.platform == "linux":
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", "$env:USERPROFILE"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                win_home = result.stdout.strip()
                if win_home:
                    dirs.append(Path(win_home) / ".codex" / "sessions")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        # Fallback: check common mount points
        users_dir = Path("/mnt/c/Users")
        if users_dir.exists():
            for mnt in users_dir.glob("*"):
                if not mnt.is_dir():
                    continue
                try:
                    cand = mnt / ".codex" / "sessions"
                    if cand.is_dir():
                        dirs.append(cand)
                except PermissionError:
                    continue

    SESSION_DIRS = dirs
    return SESSION_DIRS


def find_rollouts():
    """Scan session dirs for rollout-*.jsonl files. Return sorted list of Paths."""
    files = []
    for sess_dir in find_session_dirs():
        try:
            if not sess_dir.exists():
                continue
        except PermissionError:
            continue
        try:
            for year in sess_dir.iterdir():
                try:
                    if not year.is_dir() or not re.match(r"^\d{4}$", year.name):
                        continue
                except PermissionError:
                    continue
                try:
                    for month in year.iterdir():
                        try:
                            if not month.is_dir() or not re.match(r"^\d{2}$", month.name):
                                continue
                        except PermissionError:
                            continue
                        try:
                            for day in month.iterdir():
                                try:
                                    if not day.is_dir() or not re.match(r"^\d{2}$", day.name):
                                        continue
                                except PermissionError:
                                    continue
                                try:
                                    for f in day.glob("rollout-*.jsonl"):
                                        files.append(f)
                                except PermissionError:
                                    continue
                        except PermissionError:
                            continue
                except PermissionError:
                    continue
        except PermissionError:
            continue
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _normalize_tool(name):
    """Normalize Codex tool names to standard set."""
    return TOOL_ALIASES.get(name, name)


def _dedup_key(session_id, timestamp, cumulative_total):
    return f"codex:{session_id}:{timestamp}:{cumulative_total}"


def parse_rollout(path):
    """Parse a single rollout-*.jsonl file. Return dict or None if invalid."""
    try:
        st = path.stat()
        mtime = st.st_mtime
    except OSError:
        return None

    seen_keys = set()
    session_id = ""
    model = "unknown"
    project = ""
    total_input = 0
    total_output = 0
    total_cached = 0
    total_reasoning = 0
    tool_calls = collections.Counter()
    tool_sequence = []
    shell_commands = []
    first_ts = None
    last_ts = None
    first_line = True
    is_codex = False
    date_str = ""

    # Extract date from path: sessions/YYYY/MM/DD/
    parts = path.parts
    for i, p in enumerate(parts):
        if p == "sessions" and i + 3 < len(parts):
            try:
                y, m, d = parts[i + 1], parts[i + 2], parts[i + 3]
                if re.match(r"^\d{4}$", y) and re.match(r"^\d{2}$", m) and re.match(r"^\d{2}$", d):
                    date_str = f"{y}-{m}-{d}"
            except (IndexError, ValueError):
                pass

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                etype = entry.get("type", "")

                # First line: validate it's a Codex session
                if first_line:
                    first_line = False
                    if etype == "session_meta":
                        meta_payload = entry.get("payload") or {}
                        originator = str(meta_payload.get("originator", "")).lower()
                        if originator.startswith("codex"):
                            is_codex = True
                            session_id = meta_payload.get("session_id") or str(path.name)
                            project = meta_payload.get("cwd") or ""
                            model = meta_payload.get("model") or ""
                            if not model or model == "unknown":
                                model = meta_payload.get("agent_type") or ""
                            # Extract model from base_instructions text if not found directly
                            if not model or model == "unknown":
                                bi = meta_payload.get("base_instructions") or {}
                                bi_text = bi.get("text") if isinstance(bi, dict) else str(bi)
                                m = re.search(r'based on\s+([\w\.\-]+)', bi_text)
                                if m:
                                    model = m.group(1).strip().rstrip(".")
                            if not model:
                                model = "unknown"
                        else:
                            return None
                    # If no explicit originator, still try (some older format)
                    elif etype == "event_msg":
                        payload = entry.get("payload") or {}
                        if payload.get("type") == "token_count":
                            is_codex = True
                            session_id = entry.get("session_id", str(path.name))

                if not is_codex:
                    continue

                # Token count events
                if etype == "event_msg":
                    payload = entry.get("payload") or {}
                    ptype = payload.get("type")

                    if ptype == "token_count":
                        info = payload.get("info") or {}
                        usage = info.get("total_token_usage") or {}
                        if usage:
                            ts = entry.get("timestamp", 0)
                            cum_total = usage.get("total_tokens", 0)
                            key = _dedup_key(session_id, ts, cum_total)
                            if key in seen_keys:
                                continue
                            seen_keys.add(key)

                            last = info.get("last_token_usage") or {}
                            if last:
                                inp = last.get("input_tokens", 0)
                                out = last.get("output_tokens", 0)
                                cached = last.get("cached_input_tokens", 0)
                                reasoning = last.get("reasoning_output_tokens", 0)
                            else:
                                inp = usage.get("input_tokens", 0)
                                out = usage.get("output_tokens", 0)
                                cached = usage.get("cached_input_tokens", 0)
                                reasoning = usage.get("reasoning_output_tokens", 0)

                            # OpenAI counts cached inside input — subtract
                            if cached > 0 and inp >= cached:
                                inp = inp - cached

                            total_input += inp
                            total_output += out
                            total_cached += cached
                            total_reasoning += reasoning

                            try:
                                ts_num = float(ts)
                            except (TypeError, ValueError):
                                ts_num = 0
                            if first_ts is None:
                                first_ts = ts_num
                            last_ts = ts_num

                    elif ptype == "function_call":
                        payload_args = payload.get("arguments") or {}
                        tool_name = _normalize_tool(payload.get("name") or "unknown")
                        tool_calls[tool_name] += 1
                        try:
                            ts_num = float(entry.get("timestamp") or 0)
                        except (TypeError, ValueError):
                            ts_num = 0
                        tool_sequence.append({
                            "tool": tool_name,
                            "ts": ts_num,
                        })
                        if tool_name == "Bash":
                            cmd = payload_args.get("command") or ""
                            if cmd:
                                shell_commands.append(cmd)

                    elif ptype == "mcp_tool_call_end":
                        inv = payload.get("invocation") or {}
                        mcp_server = inv.get("server") or ""
                        mcp_tool = inv.get("tool") or ""
                        raw_tool = f"{mcp_server}:{mcp_tool}"
                        tool_name = MCP_TOOL_ALIASES.get(mcp_tool, raw_tool)
                        tool_calls[tool_name] += 1
                        try:
                            ts_num = float(entry.get("timestamp") or 0)
                        except (TypeError, ValueError):
                            ts_num = 0
                        tool_sequence.append({
                            "tool": tool_name,
                            "ts": ts_num,
                        })
                        if tool_name == "Bash":
                            args = inv.get("arguments") or {}
                            cmd = args.get("command") or args.get("cmd") or ""
                            if cmd:
                                shell_commands.append(cmd)

    except (IOError, json.JSONDecodeError):
        return None

    if not is_codex:
        return None

    total_tokens = total_input + total_output + total_cached + total_reasoning
    duration_secs = 0
    if first_ts is not None and last_ts is not None:
        duration_secs = max(0, last_ts - first_ts)

    return {
        "key": str(path.resolve()),
        "filename": path.name,
        "date": date_str,
        "mtime": mtime,
        "session_id": session_id,
        "model": model,
        "project": project,
        "total_input": total_input,
        "total_output": total_output,
        "total_cached": total_cached,
        "total_reasoning": total_reasoning,
        "total_tokens": total_tokens,
        "tool_calls": dict(tool_calls),
        "tool_calls_list": tool_sequence,
        "shell_commands": shell_commands,
        "duration_secs": duration_secs,
        "activity": "",
    }


# ── Session cache ────────────────────────────────────────────────────────

session_cache = []
session_cache_lock = threading.Lock()
last_scan_time = 0
SCAN_INTERVAL = int(os.environ.get("CODEBURN_SCAN_INTERVAL", 10))


def refresh_cache():
    global session_cache, last_scan_time
    now = time.time()
    if now - last_scan_time < SCAN_INTERVAL:
        return
    files = find_rollouts()
    parsed = []
    for f in files:
        s = parse_rollout(f)
        if s:
            parsed.append(s)
    with session_cache_lock:
        session_cache = parsed
    last_scan_time = now


def get_sessions():
    refresh_cache()
    with session_cache_lock:
        return list(session_cache)


# ── Activity classification ──────────────────────────────────────────────

def classify_session(session):
    """Classify a session into one of 13 activity categories."""
    tool_calls = session.get("tool_calls", {})
    tools_set = set(tool_calls.keys())
    cmds = " ".join(session.get("shell_commands", [])).lower()
    tool_names = " ".join(tools_set).lower()

    # Conversation: zero tool calls
    if not tool_calls or sum(tool_calls.values()) == 0:
        return "Conversation"

    # Check keyword-based categories (tool usage required)
    has_edit = "Edit" in tools_set or "Write" in tools_set

    for activity, keywords in ACTIVITY_KEYWORDS.items():
        if activity == "Conversation":
            continue
        for kw in keywords:
            if kw in cmds or kw in tool_names:
                # Exploration and Planning need stricter checks
                if activity in ("Planning", "Review", "Brainstorming") and has_edit:
                    continue
                if activity in ("Testing", "Git Ops", "Build/Deploy") and not has_edit:
                    continue
                return activity

    # Tool-based classification
    if has_edit:
        # Check if there are debug-related tools
        if "Grep" in tools_set and "Bash" in tools_set:
            cmds_lower = cmds.lower()
            if any(w in cmds_lower for w in ["error", "fail", "trace", "stack"]):
                return "Debugging"
        return "Coding"

    if "Exploration" in tools_set or len(tools_set & {"Read", "Grep", "WebSearch", "Bash"}) >= 2:
        return "Exploration"

    if "Read" in tools_set or "Grep" in tools_set:
        return "Exploration"

    return "General"


def classify_all(sessions):
    for s in sessions:
        s["activity"] = classify_session(s)
    return sessions


def calc_oneshot_rates(sessions):
    """
    For each activity, compute one-shot rate.
    One-shot = no Edit->Bash->Edit retry pattern within the session.
    """
    activity_sessions = collections.defaultdict(list)
    for s in sessions:
        activity_sessions[s.get("activity", "General")].append(s)

    rates = {}
    for activity, sess_list in activity_sessions.items():
        if not sess_list:
            rates[activity] = 0.0
            continue
        oneshot_count = 0
        for s in sess_list:
            seq = s.get("tool_calls_list", [])
            tools_only = [t["tool"] for t in seq]
            has_retry = False
            for i in range(len(tools_only) - 2):
                if tools_only[i] == "Edit" and tools_only[i + 1] == "Bash" and tools_only[i + 2] == "Edit":
                    has_retry = True
                    break
            if not has_retry:
                oneshot_count += 1
        rates[activity] = round(oneshot_count / len(sess_list) * 100, 1)
    return rates


# ── Time filtering ───────────────────────────────────────────────────────

def parse_date(d):
    """Parse str to date."""
    if isinstance(d, date):
        return d
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def filter_sessions(sessions, period, from_date=None, to_date=None):
    """Filter sessions by time period."""
    today = date.today()

    if from_date and to_date:
        start = parse_date(from_date)
        end = parse_date(to_date)
    elif period == "today":
        start = today
        end = today
    elif period == "week":
        start = today - timedelta(days=6)
        end = today
    elif period == "30d":
        start = today - timedelta(days=29)
        end = today
    elif period == "month":
        start = today.replace(day=1)
        end = today
    elif period == "all":
        start = date(2020, 1, 1)
        end = today
    else:
        start = today - timedelta(days=6)
        end = today

    filtered = []
    for s in sessions:
        sd = s.get("date", "")
        if not sd:
            continue
        try:
            sd_date = datetime.strptime(sd, "%Y-%m-%d").date()
        except ValueError:
            continue
        if start <= sd_date <= end:
            filtered.append(s)

    return filtered


# ── Aggregation ──────────────────────────────────────────────────────────

def aggregate(sessions, period="week"):
    """Produce report dict from list of session dicts."""
    sessions = classify_all(sessions)
    oneshot = calc_oneshot_rates(sessions)

    n = len(sessions)
    total_input = sum(s["total_input"] for s in sessions)
    total_output = sum(s["total_output"] for s in sessions)
    total_cached = sum(s["total_cached"] for s in sessions)
    total_reasoning = sum(s["total_reasoning"] for s in sessions)
    total_tokens = sum(s["total_tokens"] for s in sessions)

    cache_hit_pct = 0.0
    combined = total_input + total_cached
    if combined > 0:
        cache_hit_pct = round(total_cached / combined * 100, 1)

    # Per-model breakdown
    model_data = collections.defaultdict(lambda: {"sessions": 0, "input": 0, "output": 0, "cached": 0, "reasoning": 0})
    for s in sessions:
        m = s.get("model", "unknown")
        model_data[m]["sessions"] += 1
        model_data[m]["input"] += s["total_input"]
        model_data[m]["output"] += s["total_output"]
        model_data[m]["cached"] += s["total_cached"]
        model_data[m]["reasoning"] += s["total_reasoning"]

    models = [
        {
            "model": m,
            "sessions": d["sessions"],
            "input": d["input"],
            "output": d["output"],
            "cached": d["cached"],
            "reasoning": d["reasoning"],
        }
        for m, d in sorted(model_data.items(), key=lambda x: sum(x[1].values()), reverse=True)
    ]

    # Per-activity breakdown
    activity_data = collections.defaultdict(lambda: {"sessions": 0, "count": 0})
    for s in sessions:
        a = s.get("activity", "General")
        activity_data[a]["sessions"] += 1

    total_activities = sum(d["sessions"] for d in activity_data.values())
    activities = [
        {
            "activity": a,
            "sessions": d["sessions"],
            "pct": round(d["sessions"] / total_activities * 100, 1) if total_activities > 0 else 0,
            "oneshot_rate": oneshot.get(a, 0),
        }
        for a, d in sorted(activity_data.items(), key=lambda x: x[1]["sessions"], reverse=True)
    ]

    # Per-tool breakdown
    tool_data = collections.Counter()
    for s in sessions:
        for t, c in s.get("tool_calls", {}).items():
            tool_data[t] += c

    total_tool_calls = sum(tool_data.values())
    tools = [
        {
            "tool": t,
            "calls": c,
            "pct": round(c / total_tool_calls * 100, 1) if total_tool_calls > 0 else 0,
        }
        for t, c in tool_data.most_common()
    ]

    # Daily breakdown
    daily_data = collections.defaultdict(lambda: {"sessions": 0, "tokens": 0})
    for s in sessions:
        d = s.get("date", "unknown")
        daily_data[d]["sessions"] += 1
        daily_data[d]["tokens"] += s["total_tokens"]

    daily = [
        {
            "date": d,
            "sessions": dd["sessions"],
            "tokens": dd["tokens"],
        }
        for d, dd in sorted(daily_data.items(), reverse=True)
    ]

    # Per-project breakdown
    project_data = collections.defaultdict(lambda: {"sessions": 0, "tokens": 0, "models": set(), "tools": collections.Counter()})
    for s in sessions:
        proj = s.get("project", "") or "unknown"
        proj_short = proj.split("\\")[-1].split("/")[-1] if proj else "unknown"
        project_data[proj_short]["sessions"] += 1
        project_data[proj_short]["tokens"] += s["total_tokens"]
        project_data[proj_short]["models"].add(s.get("model", ""))
        for t, c in s.get("tool_calls", {}).items():
            project_data[proj_short]["tools"][t] += c

    projects = [
        {
            "project": p,
            "sessions": d["sessions"],
            "tokens": d["tokens"],
            "models": list(d["models"])[:5],
        }
        for p, d in sorted(project_data.items(), key=lambda x: x[1]["tokens"], reverse=True)
    ]

    # Top sessions by tokens
    sorted_sessions = sorted(sessions, key=lambda s: s["total_tokens"], reverse=True)
    top_sessions = [
        {
            "filename": s["filename"],
            "key": s["key"],
            "date": s["date"],
            "tokens": s["total_tokens"],
            "model": s["model"],
            "activity": s.get("activity", ""),
            "duration_secs": s["duration_secs"],
        }
        for s in sorted_sessions[:5]
    ]

    return {
        "overview": {
            "sessions": n,
            "total_input": total_input,
            "total_output": total_output,
            "total_cached": total_cached,
            "total_reasoning": total_reasoning,
            "total_tokens": total_tokens,
            "cache_hit_pct": cache_hit_pct,
        },
        "models": models,
        "projects": projects,
        "activities": activities,
        "tools": tools,
        "daily": daily,
        "top_sessions": top_sessions,
        "period": period,
        "session_count": n,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── CLI formatters ───────────────────────────────────────────────────────

def _fmt(n):
    """Format number with commas."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n:,}"
    return str(n)


def _fmt_time(secs):
    if secs < 60:
        return f"{int(secs)}s"
    if secs < 3600:
        return f"{int(secs//60)}m {int(secs%60)}s"
    return f"{int(secs//3600)}h {int((secs%3600)//60)}m"


def format_status(report):
    """Compact one-liner."""
    o = report["overview"]
    period = report.get("period", "7d")
    return (
        f"Codex | {o['sessions']} sess in period | "
        f"{_fmt(o['total_input'])} in | {_fmt(o['total_output'])} out | "
        f"{_fmt(o['total_cached'])} cached | "
        f"cache {o['cache_hit_pct']}% | "
        f"{o['total_tokens']:,} total tok"
    )


def format_today(report):
    """Daily breakdown."""
    o = report["overview"]
    lines = []
    lines.append("=" * 50)
    lines.append(f"  Codex Usage — {date.today()}")
    lines.append("=" * 50)
    lines.append(f"  Sessions:    {o['sessions']}")
    lines.append(f"  Input:       {_fmt(o['total_input']):>12} tok")
    lines.append(f"  Output:      {_fmt(o['total_output']):>12} tok")
    lines.append(f"  Cached:      {_fmt(o['total_cached']):>12} tok")
    lines.append(f"  Reasoning:   {_fmt(o['total_reasoning']):>12} tok")
    lines.append(f"  Total:       {o['total_tokens']:>12,} tok")
    lines.append(f"  Cache hit:   {o['cache_hit_pct']}%")
    lines.append("")

    if report["models"]:
        lines.append("  By model:")
        for m in report["models"]:
            lines.append(f"    {m['model']:<25}  {m['sessions']} sess  "
                         f"{_fmt(m['input'])} in  {_fmt(m['output'])} out")
        lines.append("")

    if report["activities"]:
        lines.append("  By activity (1-shot):")
        for a in report["activities"]:
            osr = a['oneshot_rate']
            os_str = f"({osr}%)" if osr > 0 else ""
            lines.append(f"    {a['activity']:<20} {a['sessions']} sess  {a['pct']}%  {os_str}")
        lines.append("")

    if report["tools"]:
        top = report["tools"][:5]
        lines.append("  Top tools: " + "  ".join(f"{t['tool']}({t['calls']})" for t in top))
        lines.append("")

    return "\n".join(lines)


def format_report(report):
    """Multi-section report."""
    o = report["overview"]
    period_labels = {"today": "Today", "week": "Last 7 Days", "30d": "Last 30 Days",
                     "month": "This Month", "all": "All Time"}
    label = period_labels.get(report.get("period", "week"), report.get("period", ""))

    lines = []
    lines.append("=" * 56)
    lines.append(f"  Codex Usage Report — {label}")
    lines.append("=" * 56)
    lines.append("")
    lines.append("  Overview:")
    lines.append(f"    Sessions:      {o['sessions']}")
    lines.append(f"    Input:         {_fmt(o['total_input']):>14} tok")
    lines.append(f"    Output:        {_fmt(o['total_output']):>14} tok")
    lines.append(f"    Cached:        {_fmt(o['total_cached']):>14} tok")
    lines.append(f"    Reasoning:     {_fmt(o['total_reasoning']):>14} tok")
    lines.append(f"    Total:         {o['total_tokens']:>14,} tok")
    lines.append(f"    Cache hit:     {o['cache_hit_pct']}%")
    lines.append("")

    if report["daily"]:
        lines.append("  Daily breakdown:")
        for d in report["daily"][:14]:
            lines.append(f"    {d['date']}  {d['sessions']} sess  {_fmt(d['tokens'])} tok")
        lines.append("")

    if report["models"]:
        lines.append("  By model:")
        lines.append(f"    {'Model':<25} {'Sess':>5} {'Input':>12} {'Output':>12} {'Cached':>10}")
        lines.append(f"    {'─'*25} {'─'*5} {'─'*12} {'─'*12} {'─'*10}")
        for m in report["models"]:
            lines.append(f"    {m['model']:<25} {m['sessions']:>5} "
                         f"{_fmt(m['input']):>12} {_fmt(m['output']):>12} {_fmt(m['cached']):>10}")
        lines.append("")

    if report["activities"]:
        lines.append("  By activity (1-shot rate):")
        lines.append(f"    {'Activity':<20} {'Sess':>5} {'%':>5} {'1-shot':>8}")
        lines.append(f"    {'─'*20} {'─'*5} {'─'*5} {'─'*8}")
        for a in report["activities"]:
            os_str = f"{a['oneshot_rate']}%" if a['oneshot_rate'] > 0 else ""
            lines.append(f"    {a['activity']:<20} {a['sessions']:>5} {a['pct']:>5.1f} {os_str:>8}")
        lines.append("")

    if report["tools"]:
        lines.append("  By tool:")
        max_calls = max(t['calls'] for t in report["tools"]) if report["tools"] else 1
        for t in report["tools"]:
            bar_len = int(t['calls'] / max_calls * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"    {t['tool']:<15} {t['calls']:>6}  {bar}  {t['pct']}%")
        lines.append("")

    if report["top_sessions"]:
        lines.append("  Top sessions:")
        for s in report["top_sessions"]:
            dur = _fmt_time(s['duration_secs'])
            lines.append(f"    {s['filename']:<35}  {s['date']}  "
                         f"{_fmt(s['tokens']):>8} tok  {s['model']:<20}  {dur}  {s['activity']}")
        lines.append("")

    lines.append(f"  Generated: {report['generated']}")
    lines.append("=" * 56)
    return "\n".join(lines)


def format_json(report):
    return json.dumps(report, indent=2, default=str)


def format_csv(sessions):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "filename", "date", "model", "activity",
                      "input_tokens", "output_tokens", "cached_tokens",
                      "reasoning_tokens", "total_tokens", "duration_secs"])
    for s in sessions:
        writer.writerow([
            s.get("key", ""),
            s.get("filename", ""),
            s.get("date", ""),
            s.get("model", ""),
            s.get("activity", ""),
            s.get("total_input", 0),
            s.get("total_output", 0),
            s.get("total_cached", 0),
            s.get("total_reasoning", 0),
            s.get("total_tokens", 0),
            s.get("duration_secs", 0),
        ])
    return output.getvalue()


# ── Web dashboard server ─────────────────────────────────────────────────

def load_html():
    """Return HTML content from file or inline fallback."""
    global HTML_INLINE
    if HTML_INLINE:
        return HTML_INLINE
    if HTML_PATH.exists():
        HTML_INLINE = HTML_PATH.read_text(encoding="utf-8")
        return HTML_INLINE
    HTML_INLINE = "<html><body><h1>codeburn.html not found</h1></body></html>"
    return HTML_INLINE


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/sessions":
            self._json_response(get_sessions_data())

        elif path == "/api/report":
            period = params.get("period", ["week"])[0]
            sessions = get_sessions()
            filtered = filter_sessions(sessions, period)
            report = aggregate(filtered, period)
            self._json_response(report)

        elif path == "/api/export":
            period = params.get("period", ["week"])[0]
            fmt = params.get("format", ["json"])[0]
            sessions = get_sessions()
            filtered = filter_sessions(sessions, period)
            if fmt == "csv":
                filtered = classify_all(filtered)
                data = format_csv(filtered)
                self._text_response(data, "text/csv")
            else:
                report = aggregate(filtered, period)
                self._json_response(report)

        elif path in ("/", "/index.html"):
            html = load_html()
            self._text_response(html, "text/html; charset=utf-8")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _text_response(self, text, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, fmt, *args):
        pass


def get_sessions_data():
    """Get sessions list for API."""
    sessions = get_sessions()
    result = []
    for s in sessions:
        result.append({
            "key": s["key"],
            "filename": s["filename"],
            "date": s["date"],
            "mtime": s["mtime"],
            "model": s["model"],
            "project": s.get("project", ""),
            "total_tokens": s["total_tokens"],
            "total_input": s["total_input"],
            "total_output": s["total_output"],
            "total_cached": s["total_cached"],
            "total_reasoning": s["total_reasoning"],
            "tool_calls": s["tool_calls"],
            "activity": classify_session(s),
            "duration_secs": s["duration_secs"],
        })
    return result


def find_free_port(start=8765, max_attempts=10):
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start


def start_daemon(port, project_dir=None, force=False):
    """Start background daemon process. Use force=True to kill existing."""
    root = Path(project_dir).resolve() if project_dir else Path.cwd()
    pid_dir = root / ".codex" / "acb"
    pid_dir.mkdir(parents=True, exist_ok=True)
    pid_file = pid_dir / "codeburn.pid"
    global PID_FILE
    PID_FILE = pid_file

    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            if force:
                os.kill(pid, signal.SIGTERM)
                try:
                    os.kill(pid, 0)
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                pid_file.unlink(missing_ok=True)
            else:
                print(f"codeburn already running (PID {pid})")
                return pid
        except (ProcessLookupError, ValueError, OSError):
            pid_file.unlink(missing_ok=True)

    log_dir = root / ".run-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    out_log = log_dir / "codeburn.out.log"
    err_log = log_dir / "codeburn.err.log"
    cmd = [sys.executable, __file__, f"--port={port}", "serve"]
    if project_dir:
        cmd.insert(2, f"--project-dir={project_dir}")

    try:
        if sys.platform == "win32":
            proc = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=open(out_log, "w"), stderr=open(err_log, "w"),
            )
        else:
            proc = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=open(out_log, "w"), stderr=open(err_log, "w"),
            )
    except Exception as e:
        print(f"Failed to start daemon: {e}")
        return None

    pid_file.write_text(str(proc.pid))
    print(f"codeburn started (PID {proc.pid})")
    print(f"  http://localhost:{port}")
    print(f"  Logs: {out_log}")
    return proc.pid


def stop_daemon(project_dir=None):
    """Stop background daemon."""
    root = Path(project_dir).resolve() if project_dir else Path.cwd()
    pid_file = root / ".codex" / "acb" / "codeburn.pid"
    global PID_FILE
    PID_FILE = pid_file

    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            print(f"codeburn stopped (PID {pid})")
        except (ProcessLookupError, ValueError, OSError):
            pid_file.unlink(missing_ok=True)
            print("codeburn not running")
    else:
        print("codeburn not running")


def run_server(port):
    """Run foreground web server."""
    port = find_free_port(port)
    refresh_cache()
    print(f"\n  Anyone Can Code — Codex Usage Dashboard")
    print(f"  {'=' * 40}")
    print(f"  Server: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")
    server = socketserver.TCPServer(("127.0.0.1", port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.shutdown()


# ── CLI dispatch ─────────────────────────────────────────────────────────

def cmd_status(args):
    sessions = get_sessions()
    filtered = filter_sessions(sessions, "today")
    report_today = aggregate(filtered, "today")
    # Also get month
    month_start = date.today().replace(day=1)
    month_filtered = [s for s in sessions if s.get("date", "") >= month_start.strftime("%Y-%m-%d")]
    report_month = aggregate(month_filtered, "month")
    today_str = format_status(report_today)
    month_str = f"Month: {report_month['overview']['sessions']} sess | " \
                f"{report_month['overview']['total_tokens']:,} total tok"
    print(f"{today_str} | {month_str}")


def cmd_today(args):
    sessions = get_sessions()
    filtered = filter_sessions(sessions, "today")
    report = aggregate(filtered, "today")
    print(format_today(report))


def cmd_week(args):
    sessions = get_sessions()
    filtered = filter_sessions(sessions, "week")
    report = aggregate(filtered, "week")
    print(format_report(report))


def cmd_report(args):
    sessions = get_sessions()
    filtered = filter_sessions(sessions, args.period, args.from_date, args.to_date)
    report = aggregate(filtered, args.period)
    if args.format == "json":
        print(format_json(report))
    else:
        print(format_report(report))


def cmd_models(args):
    """Per-model token breakdown."""
    sessions = get_sessions()
    filtered = filter_sessions(sessions, args.period)
    report = aggregate(filtered, args.period)
    if args.format == "json":
        print(json.dumps({"models": report["models"]}, indent=2, default=str))
        return
    if not report["models"]:
        print("No sessions found")
        return
    top = report["models"][:args.top] if args.top else report["models"]
    print(f"\n  Models — {args.period.replace('30d','30 days').replace('_',' ')}")
    print(f"  {'─' * 60}")
    print(f"  {'Model':<25} {'Sess':>5} {'Input':>10} {'Output':>10} {'Cached':>8}")
    print(f"  {'─' * 60}")
    for m in top:
        print(f"  {m['model']:<25} {m['sessions']:>5} {fmt(m['input']):>10} {fmt(m['output']):>10} {fmt(m['cached']):>8}")
    print()


def cmd_sessions(args):
    """Per-session list."""
    sessions = get_sessions()
    filtered = filter_sessions(sessions, args.period)
    filtered = classify_all(filtered)
    if args.format == "json":
        out = []
        for s in filtered:
            out.append({
                "filename": s["filename"], "date": s["date"],
                "model": s["model"], "activity": s.get("activity",""),
                "tokens": s["total_tokens"], "duration_secs": s["duration_secs"],
                "tool_calls": s["tool_calls"],
            })
        print(json.dumps(out, indent=2, default=str))
        return
    if not filtered:
        print("No sessions found")
        return
    print(f"\n  Sessions — {args.period.replace('30d','30 days')}")
    print(f"  {'─' * 90}")
    print(f"  {'Date':<12} {'Activity':<16} {'Model':<20} {'Tokens':>10} {'Tools':<20} {'Duration':<8}")
    print(f"  {'─' * 90}")
    for s in filtered:
        tools_str = ", ".join(list(s.get("tool_calls", {}).keys())[:3])
        if len(s.get("tool_calls", {})) > 3:
            tools_str += "..."
        dur = _fmt_time(s["duration_secs"])
        print(f"  {s['date']:<12} {s.get('activity',''):<16} {s['model']:<20} {fmt(s['total_tokens']):>10} {tools_str:<20} {dur:<8}")
    print()


def cmd_daemon(args):
    start_daemon(args.port, args.project_dir, force=getattr(args, 'force', False))


def cmd_stop(args):
    stop_daemon(args.project_dir)


def cmd_serve(args):
    """Foreground server (called by daemon process)."""
    run_server(args.port)


def cmd_export(args):
    sessions = get_sessions()
    filtered = filter_sessions(sessions, args.period)
    filtered = classify_all(filtered)
    if args.format == "csv":
        print(format_csv(filtered))
    else:
        report = aggregate(filtered, args.period)
        print(format_json(report))


def main():
    parser = argparse.ArgumentParser(description="Codex token usage analyzer")
    parser.add_argument("--project-dir", help="Project root (for PID file)")
    parser.add_argument("--port", type=int, default=8765, help="Web server port")

    sub = parser.add_subparsers(dest="command", help="Subcommand")

    p_status = sub.add_parser("status", help="Compact one-liner")
    p_today = sub.add_parser("today", help="Today's breakdown")
    p_week = sub.add_parser("week", help="Last 7 days")

    p_report = sub.add_parser("report", help="Full report")
    p_report.add_argument("-p", "--period", default="week", choices=["today", "week", "30d", "month", "all"])
    p_report.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD")
    p_report.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD")
    p_report.add_argument("--format", choices=["text", "json"], default="text")

    p_daemon = sub.add_parser("daemon", help="Start web dashboard daemon")
    p_daemon.add_argument("--force", action="store_true", help="Kill existing process first")
    p_stop = sub.add_parser("stop", help="Stop web dashboard daemon")
    p_serve = sub.add_parser("serve", help="Foreground web server (internal)")

    p_export = sub.add_parser("export", help="Export session data")
    p_export.add_argument("-f", "--format", choices=["json", "csv"], default="json")
    p_export.add_argument("-p", "--period", default="week", choices=["today", "week", "30d", "month", "all"])

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "today":
        cmd_today(args)
    elif args.command == "week":
        cmd_week(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "daemon":
        cmd_daemon(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        pass
