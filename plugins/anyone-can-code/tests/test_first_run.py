import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import first_run


def test_first_run_creates_preferences_with_defaults(tmp_path):
    result = first_run.run_first_run(tmp_path, user_type="builder")
    assert result["configured"] is True
    prefs_path = tmp_path / ".codex" / "anyone-can-code" / "settings" / "preferences.json"
    assert prefs_path.exists()
    prefs = json.loads(prefs_path.read_text())
    assert prefs["communication_mode"] == "caveman-strict"
    assert prefs["user_type"] == "builder"
    assert prefs["automation_preference"] == "aggressive"


def test_developer_gets_balanced_automation(tmp_path):
    first_run.run_first_run(tmp_path, user_type="developer")
    prefs_path = tmp_path / ".codex" / "anyone-can-code" / "settings" / "preferences.json"
    prefs = json.loads(prefs_path.read_text())
    assert prefs["automation_preference"] == "balanced"


def test_first_run_is_idempotent(tmp_path):
    first_run.run_first_run(tmp_path, user_type="builder")
    first_run.run_first_run(tmp_path, user_type="developer")
    prefs_path = tmp_path / ".codex" / "anyone-can-code" / "settings" / "preferences.json"
    prefs = json.loads(prefs_path.read_text())
    assert prefs["user_type"] == "builder"


def test_first_run_not_yet_run_returns_false(tmp_path):
    assert first_run.is_configured(tmp_path) is False
    first_run.run_first_run(tmp_path, user_type="mixed")
    assert first_run.is_configured(tmp_path) is True
