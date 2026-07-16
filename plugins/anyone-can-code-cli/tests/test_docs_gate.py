import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import docs_gate


def test_hook_work_triggers_docs_gate():
    assert docs_gate.needs_docs_check("modify the SessionStart hook behavior") is True


def test_mcp_work_triggers_docs_gate():
    assert docs_gate.needs_docs_check("add a new mcp tool to the server") is True


def test_regular_work_no_docs_gate():
    assert docs_gate.needs_docs_check("add a login button to the frontend") is False


def test_docs_context_returns_web_query_when_no_local():
    ctx = docs_gate.build_docs_context("configure PreToolUse hook to block commands")
    assert "search_query" in ctx
    assert "PreToolUse" in ctx["search_query"] or "hook" in ctx["search_query"].lower()


def test_requirement_discovery_surfaces_missing():
    gaps = docs_gate.discover_missing_requirements(
        current_checklist=["frontend", "backend", "tests"],
        request="build a website with user accounts and stripe payments"
    )
    assert "auth" in gaps or "payments" in gaps
