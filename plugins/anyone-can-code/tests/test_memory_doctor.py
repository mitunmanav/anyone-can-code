import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import hardware_tier
import memory_core
import memory_doctor
import state


def test_tier_is_valid_value():
    assert hardware_tier.tier() in {"weak", "mid", "strong"}


def test_report_dead_hooks_gives_exact_fix(tmp_path):
    rep = memory_doctor.report(tmp_path)
    assert rep["hooks_alive"] is False
    assert "/hooks" in rep["fix"]
    assert "trust" in rep["fix"].lower()
    assert "restart" in rep["fix"].lower()


def test_report_alive_after_heartbeat(tmp_path):
    mem = state.ensure_project_layout(tmp_path)["memory"]
    memory_core.write_heartbeat(mem)
    rep = memory_doctor.report(tmp_path)
    assert rep["hooks_alive"] is True
    assert rep["fix"] == ""
    assert rep["backend"] in {"fts5", "like"}
    assert rep["degraded"] in {True, False}
