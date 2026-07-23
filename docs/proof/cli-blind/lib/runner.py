"""Invoke codex exec for blind proof sessions."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path


def run_codex_exec(
    *,
    project: Path,
    prompt: str,
    model: str = "gpt-5.4-mini",
    effort: str = "low",
    sandbox: str = "danger-full-access",
    codex_home: Path | None = None,
    timeout_sec: int = 600,
    bypass_hook_trust: bool = True,
    bypass_approvals: bool = True,
) -> tuple[int, str, str, dict]:
    """Return (exit_code, stdout, stderr, env_notes)."""
    cmd = [
        "codex",
        "exec",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-C",
        str(project),
        "--skip-git-repo-check",
        "--sandbox",
        sandbox,
    ]
    if bypass_approvals and sandbox == "danger-full-access":
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    if bypass_hook_trust:
        cmd.append("--dangerously-bypass-hook-trust")
    cmd.append(prompt)

    env = os.environ.copy()
    if codex_home is not None:
        env["CODEX_HOME"] = str(codex_home)

    notes = {
        "model": model,
        "model_reasoning_effort": effort,
        "sandbox": sandbox,
        "bypass_hook_trust": bypass_hook_trust,
        "bypass_approvals": bypass_approvals,
        "codex_home": str(codex_home) if codex_home else env.get("CODEX_HOME", "default"),
        "cmd": " ".join(cmd[:-1] + ["<prompt>"]),
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
            check=False,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or "", notes
    except FileNotFoundError:
        return 127, "", "codex binary not found on PATH", notes
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = (exc.stderr or "") + f"\nTIMEOUT after {timeout_sec}s"
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        return 124, out, err, notes


def init_project(project: Path) -> None:
    project.mkdir(parents=True, exist_ok=True)
    readme = project / "README.md"
    if not readme.exists():
        readme.write_text("# Habit track (blind proof project)\n", encoding="utf-8")
    git_dir = project / ".git"
    if not git_dir.exists():
        subprocess.run(
            ["git", "init"],
            cwd=project,
            capture_output=True,
            check=False,
        )
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=project,
            capture_output=True,
            check=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "start"],
            cwd=project,
            capture_output=True,
            check=False,
        )
