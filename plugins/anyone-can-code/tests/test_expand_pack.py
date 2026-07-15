"""Phase F: CLI host + other-agents later (no ACC self-audit)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import expand_pack as ep


def test_detect_host_cli():
    h = ep.detect_host({"surface": "cli"})
    assert h["id"] == "cli"
    assert h["supports_plugins"] is True


def test_detect_host_desktop():
    h = ep.detect_host({"surface": "desktop"})
    assert h["id"] == "desktop"


def test_detect_host_exec_headless():
    h = ep.detect_host({"surface": "exec"})
    assert h["id"] == "exec"
    assert "headless" in h["user_line"].lower() or "codex exec" in h["user_line"].lower()


def test_cli_howto_same_plugin_bundle():
    h = ep.cli_howto()
    assert h["id"] == "cli_port"
    assert h["cost"] == "cheap"
    assert "plugin" in h["user_line"].lower()
    assert "codex" in h["user_line"].lower()
    steps = " ".join(h["setup_steps"]).lower()
    assert "cli" in steps or "terminal" in steps or "codex" in steps


def test_other_agents_honest_later():
    h = ep.other_agents_howto()
    assert h["id"] == "other_agents"
    assert h["status"] == "later"
    assert h["force"] is False
    low = h["user_line"].lower()
    assert "later" in low or "not yet" in low or "codex first" in low
    assert "works on claude today" not in low
    assert "already ports" not in low


def test_menu_covers_phase_f():
    ids = {f["id"] for f in ep.all_features()}
    for need in ("cli_port", "other_agents"):
        assert need in ids
    assert "acc_audits_acc" not in ids
    menu = ep.plain_menu().lower()
    assert "choose" in menu or "decide" in menu
    assert "self-audit" not in menu
    assert "audits acc" not in menu


def test_no_self_audit_api():
    assert not hasattr(ep, "self_audit")
    assert not hasattr(ep, "self_audit_howto")


def test_cli_main_menu_json():
    import subprocess

    script = PLUGIN / "scripts" / "expand_pack.py"
    r = subprocess.run(
        [sys.executable, str(script), "menu", "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    ids = {item["id"] for item in data}
    assert "cli_port" in ids
    assert "other_agents" in ids
    assert "acc_audits_acc" not in ids


def test_skills_mention_cli_not_self_audit():
    status = (PLUGIN / "skills" / "status" / "SKILL.md").read_text(encoding="utf-8").lower()
    help_s = (PLUGIN / "skills" / "help" / "SKILL.md").read_text(encoding="utf-8").lower()
    blob = status + help_s
    assert "cli" in blob
    assert "self-audit" not in blob
    assert "self audit" not in blob
    assert "audits acc" not in blob
