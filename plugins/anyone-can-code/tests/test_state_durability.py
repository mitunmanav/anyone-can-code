"""Ledger durability: fsync appends, atomic rotation, torn-tail tolerant reads."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import state


def test_read_recent_jsonl_skips_torn_tail(tmp_path):
    p = tmp_path / "log.jsonl"
    state.append_jsonl(p, {"a": 1})
    state.append_jsonl(p, {"a": 2})
    with p.open("a", encoding="utf-8") as f:
        f.write('{"a": 3, "tr')  # simulated kill mid-write
    rows = state.read_recent_jsonl(p, limit=10)
    assert [r["a"] for r in rows] == [1, 2]


def test_rotation_is_atomic_no_tmp_left_and_data_kept(tmp_path):
    p = tmp_path / "log.jsonl"
    for i in range(state.JSONL_ROTATE_THRESHOLD + 10):
        state.append_jsonl(p, {"i": i})
    rows = state.read_recent_jsonl(p, limit=state.JSONL_ROTATE_KEEP + 50)
    # After mid-loop rotate to KEEP, more appends grow the file again until
    # the next threshold — so size can exceed KEEP but must stay well under
    # total-written and must retain the newest line.
    assert len(rows) < state.JSONL_ROTATE_THRESHOLD
    assert rows[-1]["i"] == state.JSONL_ROTATE_THRESHOLD + 9
    assert not list(tmp_path.glob("*.tmp")), "rotation left a tmp file behind"
    assert not list(tmp_path.glob("*.rot.tmp")), "rotation left a rot.tmp behind"


def test_append_jsonl_fsyncs(tmp_path, monkeypatch):
    import os as _os
    calls = []
    real_fsync = _os.fsync
    monkeypatch.setattr(_os, "fsync", lambda fd: (calls.append(fd), real_fsync(fd)))
    state.append_jsonl(tmp_path / "log.jsonl", {"a": 1})
    assert calls, "append_jsonl did not fsync"
