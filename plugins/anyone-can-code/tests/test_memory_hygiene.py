"""ACC wiki memory hygiene — age, secrets, never full chat.

Not Codex /memories. Scans .codex/anyone-can-code/memory/notes only.
Helper is report-only by default (no write).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))

import memory_hygiene  # noqa: E402


def _write_note(root: Path, name: str, body: str, mtime: float | None = None) -> Path:
    notes = root / ".codex" / "anyone-can-code" / "memory" / "notes" / "project"
    notes.mkdir(parents=True, exist_ok=True)
    path = notes / name
    path.write_text(body, encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def test_stale_notes_flagged_after_default_age(tmp_path: Path) -> None:
    old = time.time() - (memory_hygiene.DEFAULT_STALE_DAYS + 5) * 86400
    fresh = time.time() - 2 * 86400
    _write_note(
        tmp_path,
        "old.md",
        "---\nkind: lesson\nstatus: active\n---\n# Old\n\n## Summary\n\nOld lesson\n",
        mtime=old,
    )
    _write_note(
        tmp_path,
        "new.md",
        "---\nkind: lesson\nstatus: active\n---\n# New\n\n## Summary\n\nFresh lesson\n",
        mtime=fresh,
    )
    report = memory_hygiene.scan_memory(tmp_path)
    paths = {item["rel"] for item in report["stale"]}
    assert any("old.md" in p for p in paths)
    assert not any("new.md" in p for p in paths)
    assert report["stale_days"] == memory_hygiene.DEFAULT_STALE_DAYS


def test_secret_patterns_flagged(tmp_path: Path) -> None:
    _write_note(
        tmp_path,
        "leaky.md",
        "---\nkind: decision\nstatus: active\n---\n# Keys\n\n"
        "## Summary\n\nStore with api_key: sk-abcdefghijklmnopqrst and password=hunter2xyz\n",
    )
    report = memory_hygiene.scan_memory(tmp_path)
    assert report["secret_hits"], "must flag secret-like note body"
    hit = report["secret_hits"][0]
    assert "leaky.md" in hit["rel"]
    assert hit["kinds"]
    # Report never echoes raw secret value
    blob = json.dumps(report)
    assert "sk-abcdefghijklmnopqrst" not in blob
    assert "hunter2xyz" not in blob


def test_full_chat_rejected_for_store() -> None:
    transcript = "\n".join(
        [
            "User: hello",
            "Assistant: hi there",
            "User: do the thing",
            "Assistant: ok doing it",
            "User: more chat",
            "Assistant: still going",
            "User: and again",
            "Assistant: transcript dump",
        ]
        + [f"User: line {i}" for i in range(40)]
        + [f"Assistant: reply {i}" for i in range(40)]
    )
    result = memory_hygiene.validate_store_candidate(transcript)
    assert result["ok"] is False
    assert "full_chat" in result["reasons"]


def test_short_lesson_allowed_for_store() -> None:
    text = "Prefer pytest over ad-hoc scripts for ACC plugin tests."
    result = memory_hygiene.validate_store_candidate(text)
    assert result["ok"] is True
    assert result["reasons"] == []


def test_secret_in_candidate_not_ok_or_flagged() -> None:
    text = "Deploy with token: sk-abcdefghijklmnopqrstuvwxyz12"
    result = memory_hygiene.validate_store_candidate(text)
    assert result["ok"] is False
    assert "secret" in result["reasons"]


def test_scan_is_read_only(tmp_path: Path) -> None:
    path = _write_note(
        tmp_path,
        "keep.md",
        "---\nkind: lesson\nstatus: active\n---\n# Keep\n\n## Summary\n\nStay\n",
    )
    before = path.read_text(encoding="utf-8")
    before_mtime = path.stat().st_mtime
    memory_hygiene.scan_memory(tmp_path)
    assert path.read_text(encoding="utf-8") == before
    assert path.stat().st_mtime == before_mtime


def test_empty_memory_root_ok(tmp_path: Path) -> None:
    report = memory_hygiene.scan_memory(tmp_path)
    assert report["note_count"] == 0
    assert report["stale"] == []
    assert report["secret_hits"] == []
    assert report["full_chat_hits"] == []
    assert "memory_root" in report


def test_full_chat_note_on_disk_flagged(tmp_path: Path) -> None:
    body = (
        "---\nkind: lesson\nstatus: active\n---\n# Dump\n\n## Summary\n\n"
        + "\n".join(f"User: turn {i}\nAssistant: reply {i}" for i in range(30))
    )
    _write_note(tmp_path, "chat.md", body)
    report = memory_hygiene.scan_memory(tmp_path)
    assert report["full_chat_hits"]
    assert any("chat.md" in h["rel"] for h in report["full_chat_hits"])


def test_never_touches_codex_native_memories(tmp_path: Path) -> None:
    """ACC wiki only — path must be project ACC memory, not ~/.codex/memories."""
    report = memory_hygiene.scan_memory(tmp_path)
    root = report["memory_root"]
    assert "anyone-can-code" in root
    assert "/memories" not in root.replace("\\", "/")
    assert not root.endswith("memories")


def test_skill_registered() -> None:
    skill = PLUGIN / "skills" / "memory-hygiene" / "SKILL.md"
    assert skill.is_file()
    text = skill.read_text(encoding="utf-8")
    assert "name: memory-hygiene" in text
    assert "Use " in text.split("---", 2)[1]
    yaml_path = PLUGIN / "skills" / "memory-hygiene" / "agents" / "openai.yaml"
    ytext = yaml_path.read_text(encoding="utf-8")
    assert 'display_name: "ACC memory hygiene"' in ytext
    assert "allow_implicit_invocation: false" in ytext
    # Product line: ACC wiki, not Codex /memories
    assert "wiki" in text.lower() or "ACC" in text
    assert "/memories" in text or "not Codex" in text or "Not Codex" in text


def test_cli_json_smoke(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_note(
        tmp_path,
        "a.md",
        "---\nkind: lesson\nstatus: active\n---\n# A\n\n## Summary\n\nHi\n",
    )
    rc = memory_hygiene.main(
        ["--project-root", str(tmp_path), "--json"]
    )
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["note_count"] >= 1
