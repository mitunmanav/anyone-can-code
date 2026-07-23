from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.proof_write import write_proof


def test_proof_contains_overall_and_env(tmp_path: Path):
    sb = {
        "SessionStart": {
            "kind": "hook",
            "status": "PASS",
            "evidence": "S1",
            "notes": "",
        }
    }
    path = write_proof(
        out_dir=tmp_path,
        run_id="test-run",
        overall="FAIL",
        env={"model": "gpt-5.4-mini", "codex_home": "isolated"},
        scoreboard=sb,
        core_notes="no product yet",
        bias_notes=["unit test only"],
    )
    text = path.read_text(encoding="utf-8")
    assert "gpt-5.4-mini" in text
    assert "Overall" in text
    assert "SessionStart" in text
