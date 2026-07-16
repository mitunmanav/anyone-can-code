"""Phase E: cross-agent pickup, env adapt, model switch, headless, GH review, proof gate."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import cross_agent_pack as cap


def test_detect_env_windows_powershell():
    env = cap.detect_env({"os": "windows", "shell": "powershell"})
    assert env["windows"] is True
    assert env["shell"] == "powershell"
    assert env["package_runner"] == "npm.cmd"
    assert env["path_sep"] == "\\"
    assert env["forbid_rtk"] is True


def test_detect_env_linux_posix():
    env = cap.detect_env({"os": "linux", "shell": "bash"})
    assert env["windows"] is False
    assert env["shell"] == "posix"
    assert env["package_runner"] == "npm"
    assert env["path_sep"] == "/"
    assert env["forbid_rtk"] is True  # rtk is not a Codex Desktop tool


def test_env_agent_line_no_rtk_mentions_adapt():
    line = cap.env_agent_line(cap.detect_env({"os": "windows", "shell": "powershell"}))
    low = line.lower()
    assert "windows" in low or "powershell" in low
    assert "npm.cmd" in low
    assert "rtk" not in low or "no rtk" in low or "not rtk" in low
    # must warn against unix-only assumptions
    assert "bash" in low or "||" in line or "unix" in low or "adapt" in low


def test_pickup_howto_wraps_native_not_rebuild():
    h = cap.pickup_howto()
    assert h["cost"] == "cheap"
    assert "handoff" in h["native"].lower() or "resume" in h["native"].lower()
    assert "thread/start" in h["agent_line"].lower() or "handoff" in h["agent_line"].lower()
    assert "choose" in h["user_line"].lower() or "decide" in h["user_line"].lower()


def test_model_switch_prefers_new_thread_for_big_swap():
    h = cap.model_switch_howto()
    assert "/model" in h["native"] or "composer" in h["native"].lower()
    assert "new" in h["user_line"].lower()
    assert "handoff" in h["user_line"].lower() or "handoff" in h["agent_line"].lower()
    text = cap.format_model_switch_prompt(
        goal="finish login",
        model="gpt-5.6",
        reasoning="medium",
        next_action="write tests",
    )
    assert "gpt-5.6" in text
    assert "medium" in text.lower()
    assert "login" in text.lower()
    assert "caveman" in text.lower()


def test_headless_wraps_codex_exec():
    h = cap.headless_howto()
    assert "codex exec" in h["native"]
    assert "read-only" in h["user_line"].lower() or "safe" in h["user_line"].lower()
    cmd = cap.format_headless_command("summarize this repo", sandbox="workspace-write", json_out=True)
    assert cmd.startswith("codex exec")
    assert "workspace-write" in cmd
    assert "--json" in cmd
    assert "summarize" in cmd


def test_github_review_wraps_native_settings():
    h = cap.github_review_howto()
    assert "codex" in h["native"].lower()
    assert "@codex review" in h["user_line"] or "@codex review" in str(h.get("setup_steps"))
    assert "automatic" in h["user_line"].lower() or "auto" in h["user_line"].lower()
    assert h["force"] is False
    assert "cloud" in h["user_line"].lower() or "cloud" in str(h.get("setup_steps")).lower()


def test_proof_gate_blocks_done_without_evidence():
    gate = cap.claim_done({})
    assert gate["ok"] is False
    assert gate["missing"]
    assert "proof" in gate["user_line"].lower() or "check" in gate["user_line"].lower()


def test_proof_gate_allows_done_with_real_proof():
    gate = cap.claim_done(
        {
            "tests": "pytest -q → 10 passed",
            "interaction": "user signed in on main path",
        }
    )
    assert gate["ok"] is True
    assert not gate["missing"] or "user_accepted" in gate.get("optional_missing", [])


def test_proof_gate_rejects_unit_only_for_product_done():
    gate = cap.claim_done(
        {"tests": "unit tests pass"},
        kind="product",
    )
    assert gate["ok"] is False
    assert any("real" in m.lower() or "interaction" in m.lower() or "user" in m.lower() for m in gate["missing"])


def test_done_claim_scan_flags_fake_phrases():
    flags = cap.scan_done_claims("All done. It works perfectly. Ship it.")
    assert flags
    assert any("works" in f.lower() or "done" in f.lower() or "perfect" in f.lower() for f in flags)


def test_menu_covers_phase_e():
    ids = {f["id"] for f in cap.all_features()}
    for need in ("env_adapt", "pickup", "model_switch", "headless", "github_review", "proof_gate"):
        assert need in ids
    menu = cap.plain_menu().lower()
    assert "choose" in menu or "decide" in menu


def test_build_handoff_includes_model_when_requested(tmp_path):
    import subprocess

    script = PLUGIN / "scripts" / "build_handoff.py"
    r = subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(tmp_path),
            "--model",
            "gpt-5.6",
            "--reasoning",
            "low",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "gpt-5.6" in r.stdout
    assert "low" in r.stdout.lower()
    assert "Environment:" in r.stdout or "env" in r.stdout.lower()


def test_load_session_includes_env_line(tmp_path):
    import load_session
    import state

    state.ensure_project_layout(tmp_path)
    ctx = load_session.build_context(tmp_path, "startup")
    low = ctx.lower()
    assert "env:" in low or "environment:" in low or "windows" in low or "linux" in low or "posix" in low
    # never push rtk as required
    assert "use rtk" not in low


def test_skills_carry_phase_e_rules():
    orch = (PLUGIN / "skills" / "orchestrator" / "SKILL.md").read_text(encoding="utf-8").lower()
    handoff = (PLUGIN / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8").lower()
    verify = (PLUGIN / "skills" / "verify" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "proof" in orch or "proof" in verify
    assert "model" in handoff or "handoff" in handoff
    assert "codex exec" in orch or "headless" in orch or "codex exec" in verify
    assert "@codex review" in orch or "github" in orch or "@codex review" in verify
