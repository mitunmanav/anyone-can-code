from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.scenarios import load_scenarios, assert_no_coaching


def test_scenarios_load_eight():
    items = load_scenarios(ROOT / "scenarios.json")
    assert len(items) >= 8
    assert items[0]["id"] == "S1"


def test_no_coaching_in_prompts():
    items = load_scenarios(ROOT / "scenarios.json")
    assert_no_coaching(items)
