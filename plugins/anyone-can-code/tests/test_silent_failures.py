import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import silent_failure_detector


def test_empty_output_is_silent_failure():
    result = silent_failure_detector.scan_tool_response({"output": "", "exit_code": 0})
    assert "empty output with exit 0" in " ".join(result["silent_failures"]).lower()


def test_json_null_result_is_silent_failure():
    result = silent_failure_detector.scan_tool_response({"output": "null", "exit_code": 0})
    assert result["silent_failures"]


def test_success_with_warning_lines_flagged():
    result = silent_failure_detector.scan_tool_response({
        "output": "Tests passed.\nWARNING: 3 tests skipped.",
        "exit_code": 0,
    })
    assert any("warning" in f.lower() or "skip" in f.lower() for f in result["silent_failures"])


def test_clean_output_no_silent_failures():
    result = silent_failure_detector.scan_tool_response({
        "output": "All 15 tests passed.",
        "exit_code": 0,
    })
    assert result["silent_failures"] == []


def test_nonzero_exit_not_silent():
    result = silent_failure_detector.scan_tool_response({"output": "Error", "exit_code": 1})
    assert result["silent_failures"] == []
