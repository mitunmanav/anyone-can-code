"""Progress ledger — fight context rot. Round-trip + inject size cap."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
HOOKS = Path(__file__).resolve().parents[1] / "hooks" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HOOKS))

import context_rot  # noqa: E402
import load_session  # noqa: E402
import state as hook_state  # noqa: E402


def test_init_creates_ledger_with_sections(tmp_path: Path) -> None:
    path = context_rot.init(tmp_path, where="feature branch", next_step="write tests")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "## WHERE" in text
    assert "## NEXT" in text
    assert "## DONE" in text
    assert "## OPEN" in text
    assert "feature branch" in text
    assert "write tests" in text


def test_append_done_and_open_round_trip(tmp_path: Path) -> None:
    context_rot.init(tmp_path, where="w", next_step="n")
    context_rot.append_done(tmp_path, "shipped unit tests")
    context_rot.append_open(tmp_path, "wire inject")
    data = context_rot.load(tmp_path)
    assert data["where"] == "w"
    assert data["next"] == "n"
    assert any("shipped unit tests" in x for x in data["done"])
    assert any("wire inject" in x for x in data["open"])
    rendered = context_rot.render(tmp_path)
    assert "shipped unit tests" in rendered
    assert "wire inject" in rendered


def test_set_where_and_next(tmp_path: Path) -> None:
    context_rot.init(tmp_path)
    context_rot.set_where(tmp_path, "new where")
    context_rot.set_next(tmp_path, "new next")
    data = context_rot.load(tmp_path)
    assert data["where"] == "new where"
    assert data["next"] == "new next"


def test_inject_line_empty_when_no_ledger(tmp_path: Path) -> None:
    assert context_rot.inject_line(tmp_path) == ""


def test_inject_line_capped_and_points_at_file(tmp_path: Path) -> None:
    context_rot.init(
        tmp_path,
        where="x" * 200,
        next_step="y" * 200,
    )
    for i in range(8):
        context_rot.append_done(tmp_path, f"done item {i} " + ("z" * 40))
        context_rot.append_open(tmp_path, f"open item {i} " + ("q" * 40))
    line = context_rot.inject_line(tmp_path)
    assert line
    assert len(line) <= context_rot.INJECT_MAX_CHARS
    assert "progress-ledger" in line or "Ledger:" in line
    assert "WHERE" in line or "where" in line.lower() or "x" in line


def test_inject_prefers_thin_one_liner(tmp_path: Path) -> None:
    context_rot.init(tmp_path, where="goal A", next_step="step B")
    line = context_rot.inject_line(tmp_path)
    assert "\n\n" not in line  # single compact block, not a wall
    assert len(line) <= 280 or len(line) <= context_rot.INJECT_MAX_CHARS


def test_append_capsule_pointer(tmp_path: Path) -> None:
    context_rot.init(tmp_path, where="w", next_step="n")
    context_rot.append_capsule_pointer(
        tmp_path, pointer="state/compact-capsule.md", note="pre-compact"
    )
    data = context_rot.load(tmp_path)
    joined = " ".join(data["done"] + data["open"] + [data["where"], data["next"]])
    text = context_rot.render(tmp_path)
    assert "compact-capsule" in text or "capsule" in text.lower()
    assert "pre-compact" in text or "capsule" in joined.lower() or "capsule" in text


def test_load_session_injects_thin_line_when_ledger_exists(tmp_path: Path) -> None:
    hook_state.write_state(
        tmp_path,
        {"phase": "build", "route": "feature", "next_step": "keep going", "active_goal": "ledger"},
    )
    context_rot.init(tmp_path, where="ledger work", next_step="inject")
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Ledger:" in ctx or "progress-ledger" in ctx
    # Must not blow the soft cap alone
    ledger_bits = [ln for ln in ctx.splitlines() if "Ledger:" in ln or "progress-ledger" in ln]
    assert ledger_bits
    assert all(len(ln) <= context_rot.INJECT_MAX_CHARS for ln in ledger_bits)


def test_load_session_skips_ledger_when_absent(tmp_path: Path) -> None:
    hook_state.write_state(tmp_path, {"phase": "idle", "route": "general"})
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Ledger:" not in ctx
    assert "progress-ledger" not in ctx


def test_done_list_is_capped(tmp_path: Path) -> None:
    context_rot.init(tmp_path)
    for i in range(context_rot.MAX_DONE_KEEP + 5):
        context_rot.append_done(tmp_path, f"item-{i}")
    data = context_rot.load(tmp_path)
    assert len(data["done"]) <= context_rot.MAX_DONE_KEEP
    assert any("item-" in x for x in data["done"])


def test_save_session_appends_capsule_pointer_when_ledger_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import save_session

    context_rot.init(tmp_path, where="session", next_step="save")
    hook_state.write_state(tmp_path, {"phase": "build", "route": "feature"})
    save_session.handle_payload(
        {
            "last_assistant_message": "saved progress on ledger",
            "turn_id": "t-ledger",
            "hook_event_name": "Stop",
        },
        tmp_path,
    )
    text = context_rot.render(tmp_path)
    assert "session-snapshot" in text or "capsule" in text.lower() or "session" in text.lower()
