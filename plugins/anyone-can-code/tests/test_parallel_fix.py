"""Parser + skill registration for $parallel-fix (multi-file test fan-out)."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import parallel_fix  # noqa: E402


SAMPLE_PYTEST = """
============================= test session starts ==============================
collected 12 items

tests/test_a.py::test_one PASSED
tests/test_b.py::test_two FAILED
tests/test_c.py::test_three ERROR
tests/test_b.py::test_four FAILED
tests/test_d.py::test_five PASSED

=================================== FAILURES ===================================
_______________________________ test_two _______________________________________
AssertionError: boom
==================================== ERRORS ====================================
________________________ ERROR at setup of test_three __________________________
RuntimeError: setup
=========================== short test summary info ============================
FAILED tests/test_b.py::test_two - AssertionError: boom
FAILED tests/test_b.py::test_four - AssertionError: again
ERROR tests/test_c.py::test_three - RuntimeError: setup
==================== 2 failed, 1 error, 9 passed in 0.12s ======================
"""


def test_parse_unique_files_stable_order() -> None:
    files = parallel_fix.parse_failed_files(SAMPLE_PYTEST)
    assert files == ["tests/test_b.py", "tests/test_c.py"]


def test_parse_empty_on_all_green() -> None:
    green = "============================== 5 passed in 0.01s ==============================="
    assert parallel_fix.parse_failed_files(green) == []


def test_parse_windows_and_abs_paths() -> None:
    text = (
        "FAILED C:\\repo\\tests\\test_win.py::test_x - assert False\n"
        "FAILED /home/u/proj/tests/test_abs.py::test_y - boom\n"
    )
    files = parallel_fix.parse_failed_files(text)
    assert "tests/test_win.py" in files or files[0].endswith("test_win.py")
    assert any(p.endswith("test_abs.py") for p in files)


def test_parse_ignores_non_failed_lines() -> None:
    text = (
        "PASSED tests/test_ok.py::test_a\n"
        "tests/test_ok.py::test_b PASSED\n"
        "SKIPPED [1] tests/test_skip.py:1: reason\n"
    )
    assert parallel_fix.parse_failed_files(text) == []


def test_cli_stdin_one_path_per_line(capsys) -> None:
    code = parallel_fix.main(["-"], SAMPLE_PYTEST)
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == ["tests/test_b.py", "tests/test_c.py"]


def test_cli_json_mode(capsys) -> None:
    code = parallel_fix.main(["--json", "-"], SAMPLE_PYTEST)
    assert code == 0
    import json

    assert json.loads(capsys.readouterr().out) == [
        "tests/test_b.py",
        "tests/test_c.py",
    ]


def test_skill_frontmatter_and_display_name() -> None:
    skill_md = (PLUGIN / "skills" / "parallel-fix" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "name: parallel-fix" in skill_md
    assert "subagent" in skill_md.lower()
    yaml_text = (
        PLUGIN / "skills" / "parallel-fix" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert 'display_name: "ACC parallel fix"' in yaml_text
    assert "allow_implicit_invocation: false" in yaml_text


def test_skill_under_budget() -> None:
    size = len((PLUGIN / "skills" / "parallel-fix" / "SKILL.md").read_text(encoding="utf-8"))
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
