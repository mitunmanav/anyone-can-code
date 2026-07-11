import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import comm_contract


def test_caveman_strict_strips_filler():
    result = comm_contract.apply_tone(
        "I have successfully completed the implementation of the requested feature.",
        mode="caveman-strict",
    )
    assert "I have successfully" not in result
    assert len(result) < 80


def test_caveman_strict_is_default():
    result = comm_contract.apply_tone("Feature done.", mode=None)
    assert result


def test_normal_mode_preserves_text():
    text = "The authentication module has been updated."
    result = comm_contract.apply_tone(text, mode="normal")
    assert result == text


def test_skill_banner_always_caveman():
    banner = comm_contract.skill_banner("plan", mode="normal")
    assert "Plan:" in banner
    assert len(banner) < 60
