"""Kill a durable writer at random offsets; state must parse, ledger loses at most the torn tail.

Default 15 iterations to keep the gate fast. Deep run: ACC_KILLTEST_ITERS=200.
"""
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import state

WRITER = Path(__file__).resolve().parent / "killtest_writer.py"
ITERS = int(os.environ.get("ACC_KILLTEST_ITERS", "15"))


def test_kill_writer_never_corrupts_state(tmp_path):
    rng = random.Random(1234)
    for iteration in range(ITERS):
        work = tmp_path / f"run{iteration}"
        work.mkdir()
        proc = subprocess.Popen([sys.executable, str(WRITER), str(work)])
        time.sleep(rng.uniform(0.05, 0.4))
        proc.kill()
        proc.wait(timeout=10)

        now = work / "now.json"
        if now.exists():
            parsed = json.loads(now.read_text(encoding="utf-8"))  # must never be torn
            assert "goal" in parsed
        events = work / "events.jsonl"
        if events.exists():
            lines = events.read_text(encoding="utf-8").splitlines()
            torn = 0
            for idx, line in enumerate(lines):
                try:
                    json.loads(line)
                except ValueError:
                    torn += 1
                    assert idx == len(lines) - 1, "torn line not at tail — ledger corrupted"
            assert torn <= 1
            rows = state.read_recent_jsonl(events, limit=10)
            if rows:
                assert isinstance(rows[-1]["i"], int)
