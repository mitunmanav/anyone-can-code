"""Memory health from NON-hook paths. This is the detector for the one
failure hooks cannot report themselves: hooks not trusted = hooks never run
= heartbeat goes stale. Runs from CLI, $setup, $status, or MCP."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hardware_tier
import memory_core
import memory_index
import state

HEARTBEAT_STALE_SECONDS = 7 * 24 * 3600  # a week without any SessionStart = dead
TRUST_FIX = (
    "Memory hooks are not running, so Anyone Can Code cannot remember this "
    "project. Fix (one time): in Codex run /hooks, trust the anyone-can-code "
    "hooks, then restart Codex. Repeat after every plugin update."
)


def report(repo_root: Path) -> dict:
    mem = state.ensure_project_layout(repo_root)["memory"]
    age = memory_core.heartbeat_age_seconds(mem)
    hooks_alive = age is not None and age < HEARTBEAT_STALE_SECONDS
    try:
        backend = memory_index.rebuild(mem)["backend"]
    except Exception:
        backend = "unavailable"
    degraded = (not hooks_alive) or backend != "fts5"
    return {
        "hooks_alive": hooks_alive,
        "heartbeat_age_s": age,
        "backend": backend,
        "tier": hardware_tier.tier(),
        "degraded": degraded,
        "fix": "" if hooks_alive else TRUST_FIX,
    }


def main() -> None:
    root = Path.cwd()
    rep = report(root)
    if "--json" in sys.argv:
        print(json.dumps(rep, indent=2))
        return
    print(f"Memory: {'OK' if rep['hooks_alive'] else 'NOT RUNNING'}")
    print(f"Search backend: {rep['backend']} (tier: {rep['tier']})")
    if rep["fix"]:
        print(rep["fix"])


if __name__ == "__main__":
    main()
