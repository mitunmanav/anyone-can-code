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


def test_jargon_becomes_plain_words():
    result = comm_contract.apply_tone(
        "We added RLS so tenant isolation is enforced.", mode="caveman-strict"
    )
    low = result.lower()
    assert "rls" not in low
    assert "tenant isolation" not in low


def test_two_sentence_help_is_kept_warm():
    text = (
        "Making the login page now. "
        "It will have email and password fields for your users to sign in."
    )
    result = comm_contract.apply_tone(text, mode="caveman-strict")
    low = result.lower()
    assert "login page" in low
    assert "email and password" in low  # 2nd sentence survives — no cold amputation


def test_normal_mode_still_untouched():
    text = "We enabled RLS for tenant isolation."
    assert comm_contract.apply_tone(text, mode="normal") == text
