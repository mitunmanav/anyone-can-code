"""Safety item 26: production security gate before deploy."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import security_gate


def test_clean_project_passes(tmp_path):
    (tmp_path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    result = security_gate.scan_project(tmp_path)
    assert result["ok"] is True
    assert result["findings"] == []


def test_open_signup_and_admin123_fail(tmp_path):
    (tmp_path / "config.py").write_text(
        'ALLOW_PUBLIC_REGISTRATION = "true"\nDEFAULT_ADMIN_PASSWORD = "admin123"\n',
        encoding="utf-8",
    )
    result = security_gate.scan_project(tmp_path)
    assert result["ok"] is False
    ids = {f["id"] for f in result["findings"]}
    assert "open_signup" in ids
    assert "default_password" in ids
    assert "do not ship" in result["user_line"].lower() or "fail" in result["user_line"].lower()


def test_placeholder_secret_fail(tmp_path):
    (tmp_path / ".env").write_text("API_KEY=changeme\n", encoding="utf-8")
    result = security_gate.scan_project(tmp_path)
    assert result["ok"] is False
    assert any(f["id"] == "placeholder_secret" for f in result["findings"])


def test_guard_blocks_deploy_when_gate_fails(tmp_path, monkeypatch):
    import sys
    from pathlib import Path as P

    hooks = P(__file__).resolve().parents[1] / "hooks" / "scripts"
    sys.path.insert(0, str(hooks))
    import guard

    (tmp_path / "config.py").write_text(
        'ALLOW_PUBLIC_REGISTRATION = "true"\nDEFAULT_ADMIN_PASSWORD = "admin123"\n',
        encoding="utf-8",
    )
    monkeypatch.delenv("USE_MOCK_DB", raising=False)
    out = guard.handle_payload(
        {
            "hook_event_name": "PreToolUse",
            "tool_input": {"command": "vercel deploy --prod"},
        },
        tmp_path,
    )
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
    assert decision == "deny"
    reason = out["hookSpecificOutput"]["permissionDecisionReason"].lower()
    assert "security gate" in reason
