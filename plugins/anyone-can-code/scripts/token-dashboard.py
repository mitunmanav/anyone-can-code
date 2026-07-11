#!/usr/bin/env python3
"""
token-dashboard.py — Live token usage web dashboard for Codex Desktop.

Serves a local HTTP server on port 8765 that shows live token usage
by parsing Codex session rollout files from ~/.codex/sessions/.

Usage:
    python token-dashboard.py                     # Start server (blocking)
    python token-dashboard.py --daemon            # Start as background daemon
    python token-dashboard.py --stop              # Stop running daemon
    python token-dashboard.py --port 8080         # Custom port
    python token-dashboard.py --project-dir PATH  # Project root override
"""

import argparse
import collections
import http.server
import json
import os
import signal
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs


HTML_PATH = Path(__file__).parent / "token-dashboard.html"
SESSION_DIR = Path.home() / ".codex" / "sessions"
REFRESH_INTERVAL = 3
TOOL_LOG_PATH = None
PID_FILE = None


def find_repo_root():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.cwd()


def resolve_paths(project_dir=None):
    global TOOL_LOG_PATH, PID_FILE
    root = Path(project_dir).resolve() if project_dir else find_repo_root()
    acb_dir = root / ".codex" / "acb"
    acb_dir.mkdir(parents=True, exist_ok=True)
    TOOL_LOG_PATH = acb_dir / "tool-usage.jsonl"
    PID_FILE = acb_dir / "dashboard.pid"


def read_tool_usage_log():
    if not TOOL_LOG_PATH or not TOOL_LOG_PATH.exists():
        return {"tool_counts": {}, "recent_count": 0, "total_entries": 0}
    tool_counts = collections.Counter()
    recent_entries = []
    try:
        with open(TOOL_LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    tool_name = entry.get("tool_name", "unknown")
                    tool_counts[tool_name] += 1
                    recent_entries.append(entry)
                except json.JSONDecodeError:
                    continue
        recent_entries = recent_entries[-20:]
        return {
            "tool_counts": dict(tool_counts.most_common()),
            "recent_entries": recent_entries,
            "recent_count": len(recent_entries),
            "total_entries": sum(tool_counts.values()),
        }
    except Exception:
        return {"tool_counts": {}, "recent_count": 0, "total_entries": 0}


def parse_rollout_file(filepath):
    data = {
        "total_input": 0, "total_output": 0, "total_cached": 0,
        "total_reasoning": 0, "total_tokens": 0, "tool_calls": {},
    }
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "event_msg":
                    continue
                payload = entry.get("payload", {})
                ptype = payload.get("type")
                if ptype == "token_count":
                    info = payload.get("info", {})
                    usage = info.get("total_token_usage", {})
                    if usage:
                        data["total_input"] += usage.get("input_tokens", 0)
                        data["total_output"] += usage.get("output_tokens", 0)
                        data["total_cached"] += usage.get("cached_input_tokens", 0)
                        data["total_reasoning"] += usage.get("reasoning_output_tokens", 0)
                        data["total_tokens"] += usage.get("total_tokens", 0)
                elif ptype == "function_call":
                    tool_name = payload.get("name", "unknown")
                    data["tool_calls"][tool_name] = data["tool_calls"].get(tool_name, 0) + 1
    except (IOError, json.JSONDecodeError):
        pass
    return data


def list_all_sessions():
    if not SESSION_DIR.exists():
        return []
    files = sorted(
        SESSION_DIR.rglob("rollout-*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    sessions = []
    for i, f in enumerate(files):
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(f.stat().st_mtime))
        size = f.stat().st_size
        data = parse_rollout_file(f)
        sessions.append({
            "key": str(f.resolve()),
            "filename": f.name,
            "mtime": mtime,
            "size": size,
            "total_tokens": data["total_tokens"],
            "total_input": data["total_input"],
            "total_output": data["total_output"],
            "total_cached": data["total_cached"],
            "total_reasoning": data["total_reasoning"],
            "tool_calls": data["tool_calls"],
        })
    return sessions


# Cache: list of all sessions, refreshed by background scanner
session_cache = []
session_cache_lock = threading.Lock()


def refresh_session_cache():
    global session_cache
    sessions = list_all_sessions()
    with session_cache_lock:
        session_cache = sessions


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/tokens":
            session_key = None
            if "session" in params:
                session_key = params["session"][0]
            data = self._get_session_data(session_key)
            self._json_response(data)

        elif path == "/api/tools":
            self._json_response(read_tool_usage_log())

        elif path == "/api/sessions":
            with session_cache_lock:
                self._json_response(session_cache)

        elif path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if HTML_PATH.exists():
                self.wfile.write(HTML_PATH.read_bytes())
            else:
                self.wfile.write(b"<html><body><h1>Dashboard HTML not found</h1></body></html>")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def _get_session_data(self, key):
        with session_cache_lock:
            if not session_cache:
                return {"total_tokens": 0, "session_count": 0, "current_session": 0}
            if key is None:
                entry = session_cache[0]
            else:
                found = [e for e in session_cache if e["key"] == key]
                entry = found[0] if found else session_cache[0]
            return {
                "total_input": entry["total_input"],
                "total_output": entry["total_output"],
                "total_cached": entry["total_cached"],
                "total_reasoning": entry["total_reasoning"],
                "total_tokens": entry["total_tokens"],
                "tool_calls": entry["tool_calls"],
                "session_count": len(session_cache),
                "current_session_key": entry["key"],
                "last_updated": time.strftime("%H:%M:%S"),
            }

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


def background_scanner():
    while True:
        refresh_session_cache()
        time.sleep(REFRESH_INTERVAL)


def find_free_port(start=8765, max_attempts=10):
    import socket
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return start


def start_daemon(port, project_dir):
    if PID_FILE and PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            print(f"Dashboard already running (PID {pid})")
            return pid
        except (ProcessLookupError, ValueError, OSError):
            PID_FILE.unlink(missing_ok=True)
    log_dir = Path.cwd() / ".run-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    out_log = log_dir / "token-dashboard.out.log"
    err_log = log_dir / "token-dashboard.err.log"
    cmd = [sys.executable, __file__, f"--port={port}"]
    if project_dir:
        cmd.append(f"--project-dir={project_dir}")
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
    if PID_FILE:
        PID_FILE.write_text(str(proc.pid))
    print(f"Dashboard started (PID {proc.pid})")
    print(f"  http://localhost:{port}")
    print(f"  Logs: {out_log}")
    return proc.pid


def stop_daemon():
    if PID_FILE and PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            PID_FILE.unlink()
            print(f"Dashboard stopped (PID {pid})")
        except (ProcessLookupError, ValueError, OSError):
            PID_FILE.unlink(missing_ok=True)
            print("Dashboard not running")
    else:
        print("Dashboard not running")


def run_server(port):
    port = find_free_port(port)
    scanner = threading.Thread(target=background_scanner, daemon=True)
    scanner.start()
    refresh_session_cache()
    print(f"\n  Anyone Can Code — Token Dashboard")
    print(f"  {'=' * 35}")
    print(f"  Server: http://localhost:{port}")
    print(f"  Sessions: {SESSION_DIR}")
    print(f"  Tool log: {TOOL_LOG_PATH}")
    print(f"  Press Ctrl+C to stop\n")
    server = socketserver.TCPServer(("", port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Anyone Can Code — Token Dashboard")
    parser.add_argument("--port", type=int, default=8765, help="Port to serve on")
    parser.add_argument("--daemon", action="store_true", help="Start as background daemon")
    parser.add_argument("--stop", action="store_true", help="Stop running daemon")
    parser.add_argument("--project-dir", help="Project root directory (auto-detect by default)")
    args = parser.parse_args()
    resolve_paths(args.project_dir)
    if args.stop:
        stop_daemon()
        return
    if args.daemon:
        pid = start_daemon(args.port, args.project_dir)
        return
    run_server(args.port)


if __name__ == "__main__":
    main()
