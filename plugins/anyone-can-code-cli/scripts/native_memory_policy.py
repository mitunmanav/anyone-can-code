#!/usr/bin/env python3
"""Item 13: keep native Codex memories OFF — ACC two-drawer is the memory.

Docs: local memories off by default; enable only via [features] memories = true.
ACC wants memories = false always in project config so native memory does not
fight ACC drawers or burn rate limits.
"""

from __future__ import annotations

import re
from pathlib import Path


MEMORIES_OFF_BLOCK = """[features]
memories = false
"""


def config_has_memories_off(text: str) -> bool:
    """True if config clearly disables native memories."""
    if re.search(r"(?m)^\s*memories\s*=\s*false\s*$", text):
        return True
    # quoted forms
    if re.search(r"(?m)^\s*memories\s*=\s*[\"']false[\"']\s*$", text):
        return True
    return False


def config_has_memories_on(text: str) -> bool:
    return bool(re.search(r"(?m)^\s*memories\s*=\s*true\s*$", text, re.I))


def ensure_memories_off(config_path: Path) -> dict:
    """Write or patch config.toml so memories = false. Returns status dict."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.write_text(MEMORIES_OFF_BLOCK + "\n", encoding="utf-8")
        return {"path": str(config_path), "action": "created", "ok": True}
    text = config_path.read_text(encoding="utf-8")
    if config_has_memories_off(text) and not config_has_memories_on(text):
        return {"path": str(config_path), "action": "already_off", "ok": True}
    if config_has_memories_on(text):
        text = re.sub(
            r"(?m)^\s*memories\s*=\s*true\s*$",
            "memories = false",
            text,
            flags=re.I,
        )
        config_path.write_text(text, encoding="utf-8")
        return {"path": str(config_path), "action": "flipped_off", "ok": True}
    if "[features]" in text:
        text = re.sub(
            r"(?m)^(\[features\]\s*)$",
            r"\1\nmemories = false",
            text,
            count=1,
        )
    else:
        text = MEMORIES_OFF_BLOCK + "\n" + text
    config_path.write_text(text, encoding="utf-8")
    return {"path": str(config_path), "action": "patched", "ok": True}


def check_memories_off(config_path: Path) -> dict:
    if not Path(config_path).exists():
        return {"ok": False, "detail": "no config.toml"}
    text = Path(config_path).read_text(encoding="utf-8")
    if config_has_memories_off(text) and not config_has_memories_on(text):
        return {"ok": True, "detail": "native memories off"}
    return {"ok": False, "detail": "native memories not off"}
