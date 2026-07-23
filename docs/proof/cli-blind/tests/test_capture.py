from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.capture import parse_hooks, parse_skill_reads, list_acc_files

SAMPLE_ERR = """
hook: SessionStart
hook: SessionStart Completed
hook: PreToolUse
hook: PreToolUse Blocked
hook: Stop
hook: Stop Completed
/bin/bash -lc 'cat /home/x/.codex/plugins/cache/anyone-can-code-marketplace/anyone-can-code/2.0.0-beta.5/skills/verify/SKILL.md'
Command blocked by PreToolUse hook: Guard stop bad command: download piped to shell
"""


def test_parse_hooks():
    h = parse_hooks(SAMPLE_ERR)
    assert "SessionStart" in h
    assert "Stop" in h
    assert "PreToolUse" in h


def test_parse_skill_reads():
    skills = parse_skill_reads(SAMPLE_ERR)
    assert "verify" in skills


def test_list_acc_files(tmp_path: Path):
    p = tmp_path / ".codex" / "anyone-can-code" / "memory" / "notes" / "x.md"
    p.parent.mkdir(parents=True)
    p.write_text("hi", encoding="utf-8")
    files = list_acc_files(tmp_path)
    assert any(str(f).endswith("x.md") for f in files)
