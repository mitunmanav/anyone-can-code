"""Item 17: cost labels."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cost_labels


def test_labels():
    assert cost_labels.label("cheap") == "[CHEAP]"
    assert cost_labels.label("hungry") == "[HUNGRY]"
    assert cost_labels.label("subagent") == "[HUNGRY]"


def test_tag_line():
    assert cost_labels.tag_line("Run free scan", "cheap").startswith("[CHEAP]")
    assert cost_labels.tag_line("Deep audit", "hungry").startswith("[HUNGRY]")
