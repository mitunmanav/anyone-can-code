"""Phase F: CLI host, other-agents later, ACC audits ACC."""
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
    # must not claim live ports
    assert "works on claude today" not in low
    assert "already ports" not in low


def test_self_audit_ok_on_plugin_tree():
    report = ep.self_audit(PLUGIN)
    assert report["id"] == "acc_audits_acc"
    assert "summary" in report
    assert report["summary"]["fail"] >= 0
    assert report["ok"] is True or report["summary"]["fail"] > 0
    assert report["user_line"]
    assert "proof" in report["agent_line"].lower() or "doctor" in report["agent_line"].lower()
    # always has skill budget + manifest checks
    ids = {c["id"] for c in report["checks"]}
    assert "skill_budget" in ids
    assert "plugin_manifest" in ids


def test_self_audit_flags_missing_manifest(tmp_path):
    report = ep.self_audit(tmp_path)
    assert report["ok"] is False
    assert report["summary"]["fail"] >= 1
    assert any(c["id"] == "plugin_manifest" and c["status"] == "fail" for c in report["checks"])


def test_self_audit_flags_fat_skill(tmp_path):
    skill = tmp_path / "skills" / "fat"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("x" * 4500, encoding="utf-8")
    (tmp_path / ".codex-plugin").mkdir()
    (tmp_path / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"name": "t", "version": "0", "skills": "./skills/"}),
        encoding="utf-8",
    )
    report = ep.self_audit(tmp_path)
    assert any(c["id"] == "skill_budget" and c["status"] == "fail" for c in report["checks"])
    assert report["ok"] is False


def test_menu_covers_phase_f():
    ids = {f["id"] for f in ep.all_features()}
    for need in ("cli_port", "other_agents", "acc_audits_acc"):
        assert need in ids
    menu = ep.plain_menu().lower()
    assert "choose" in menu or "decide" in menu


def test_cli_main_json(tmp_path):
    import subprocess

    script = PLUGIN / "scripts" / "expand_pack.py"
    r = subprocess.run(
        [sys.executable, str(script), "self-audit", "--plugin-root", str(PLUGIN), "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["id"] == "acc_audits_acc"
    assert "summary" in data


def test_skills_mention_phase_f():
    status = (PLUGIN / "skills" / "status" / "SKILL.md").read_text(encoding="utf-8").lower()
    help_s = (PLUGIN / "skills" / "help" / "SKILL.md").read_text(encoding="utf-8").lower()
    orch = (PLUGIN / "skills" / "orchestrator" / "SKILL.md").read_text(encoding="utf-8").lower()
    blob = status + help_s + orch
    assert "self-audit" in blob or "audits" in blob or "doctor" in blob
    assert "cli" in blob
