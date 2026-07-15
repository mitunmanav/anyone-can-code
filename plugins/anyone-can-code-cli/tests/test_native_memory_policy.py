"""Item 13: native Codex memory stays OFF."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import native_memory_policy as nmp


def test_reference_config_has_memories_false():
    text = (PLUGIN / "reference" / "project" / ".codex" / "config.toml").read_text(
        encoding="utf-8"
    )
    assert nmp.config_has_memories_off(text)


def test_ensure_creates_and_flips(tmp_path):
    path = tmp_path / ".codex" / "config.toml"
    r1 = nmp.ensure_memories_off(path)
    assert r1["ok"] is True
    assert nmp.check_memories_off(path)["ok"] is True

    path.write_text("[features]\nmemories = true\n", encoding="utf-8")
    r2 = nmp.ensure_memories_off(path)
    assert r2["action"] == "flipped_off"
    assert "memories = false" in path.read_text(encoding="utf-8")
