"""Subprocess target for kill-tests. Loops durable writes until killed.

Usage: python3 killtest_writer.py <workdir>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "scripts"))
import memory_core
import state

def main() -> None:
    work = Path(sys.argv[1])
    i = 0
    while True:
        i += 1
        state.append_jsonl(work / "events.jsonl", {"i": i})
        memory_core.atomic_write_text(
            work / "now.json", json.dumps({"i": i, "goal": "kill test", "next": f"step {i}"})
        )

if __name__ == "__main__":
    main()
