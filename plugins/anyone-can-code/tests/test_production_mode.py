import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import safety_receipts


def test_production_mode_requires_approval_for_more_actions():
    action = {"type": "install", "command": "npm install lodash"}
    classification_prod = safety_receipts.classify_action(action, production_mode=True)
    assert classification_prod["approval_required"] is True
    assert classification_prod.get("production_caution") is True


def test_production_mode_blocks_force_push():
    action = {"type": "push", "command": "git push --force"}
    result = safety_receipts.classify_action(action, production_mode=True)
    assert result["approval_required"] is True
    assert result.get("force_blocked") is True
