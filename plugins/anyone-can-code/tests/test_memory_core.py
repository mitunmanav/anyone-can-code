import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import memory_core


def test_scrub_redacts_secrets():
    dirty = "use api_key: sk-abcdefghijklmnop123456 and password=hunter2 ok"
    clean = memory_core.scrub(dirty)
    assert "sk-abcdefghijklmnop123456" not in clean
    assert "hunter2" not in clean
    assert "[REDACTED]" in clean


def test_scrub_keeps_normal_text():
    assert memory_core.scrub("build the waitlist site") == "build the waitlist site"


def test_atomic_write_no_tmp_left(tmp_path):
    target = tmp_path / "now.md"
    memory_core.atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
    memory_core.atomic_write_text(target, "world")
    assert target.read_text(encoding="utf-8") == "world"
    assert not list(tmp_path.glob("*.tmp"))


def test_lock_exclusive_and_stale_steal(tmp_path):
    with memory_core.memory_lock(tmp_path) as got:
        assert got is True
        with memory_core.memory_lock(tmp_path, timeout=0.2) as got2:
            assert got2 is False  # second acquirer times out, does not block forever
    # stale lock (old timestamp) gets stolen
    lock_file = tmp_path / "memory.lock"
    lock_file.write_text(json.dumps({"pid": 999999, "ts": time.time() - 999}), encoding="utf-8")
    with memory_core.memory_lock(tmp_path, timeout=0.5) as got3:
        assert got3 is True


def test_heartbeat_roundtrip(tmp_path):
    assert memory_core.heartbeat_age_seconds(tmp_path) is None
    memory_core.write_heartbeat(tmp_path)
    age = memory_core.heartbeat_age_seconds(tmp_path)
    assert age is not None and age < 5
