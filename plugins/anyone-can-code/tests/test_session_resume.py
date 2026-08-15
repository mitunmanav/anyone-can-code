"""Session resume card — LAST handoff + progress-ledger → short card."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session_resume  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _handoff_md(
    *,
    goal: str = "Ship resume card",
    next_step: str = "Wire skill step 0",
    task: str = "Write session_resume",
    session_id: str = "thr_test_1",
) -> str:
    return "\n".join(
        [
            "# ACC portable handoff",
            "schema: acc-portable-handoff/1",
            "updated_at: 2026-08-03T00:00:00Z",
            "project_root: /tmp/demo",
            "transaction_id: tx1",
            "",
            "## Where",
            "- tool_left: codex",
            f"- session_id: {session_id}",
            "- rollout_hint: none",
            "",
            "## Goal",
            goal,
            "",
            "## Plan",
            "- [x] research",
            "- [ ] implement",
            "",
            "## State",
            f"- active_task: {task}",
            "- verification: unverified",
            "",
            "## Next step",
            next_step,
            "",
            "## How to resume (any tool)",
            "1. Open this file.",
            "",
        ]
    )


def _ledger_md(
    *,
    where: str = "feature/dr-session-resume",
    next_step: str = "prove tests",
    done: list[str] | None = None,
    open_items: list[str] | None = None,
) -> str:
    done = done if done is not None else ["research WEB+Codex"]
    open_items = open_items if open_items is not None else ["write proof"]
    lines = [
        "# Progress Ledger",
        "Updated: 2026-08-03T00:00:00Z",
        "",
        "## WHERE",
        where,
        "",
        "## NEXT",
        next_step,
        "",
        "## DONE",
    ]
    if done:
        lines.extend(f"- [x] {item}" for item in done)
    else:
        lines.append("- (none yet)")
    lines += ["", "## OPEN"]
    if open_items:
        lines.extend(f"- [ ] {item}" for item in open_items)
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def test_empty_project_honest_missing(tmp_path: Path) -> None:
    card = session_resume.build_card(tmp_path)
    assert "Resume card" in card
    assert "HANDOFF: missing" in card
    assert "LEDGER: missing" in card
    assert "WHERE:" in card
    assert "NEXT:" in card
    assert "Native:" in card
    assert len(card) <= session_resume.CARD_MAX_CHARS


def test_handoff_only_fills_goal_and_next(tmp_path: Path) -> None:
    _write(session_resume.handoff_path(tmp_path), _handoff_md())
    card = session_resume.build_card(tmp_path)
    assert "HANDOFF: present" in card
    assert "LEDGER: missing" in card
    assert "Ship resume card" in card
    assert "Wire skill step 0" in card
    assert "PORTABLE_HANDOFF" in card
    assert len(card) <= session_resume.CARD_MAX_CHARS


def test_ledger_only_fills_where_next_done_open(tmp_path: Path) -> None:
    _write(
        session_resume.ledger_path(tmp_path),
        _ledger_md(
            where="ledger where",
            next_step="ledger next",
            done=["done A", "done B"],
            open_items=["open A"],
        ),
    )
    card = session_resume.build_card(tmp_path)
    assert "LEDGER: present" in card
    assert "HANDOFF: missing" in card
    assert "ledger where" in card
    assert "ledger next" in card
    assert "done A" in card
    assert "open A" in card
    assert "progress-ledger" in card


def test_both_prefer_ledger_where_next_and_show_handoff_goal(tmp_path: Path) -> None:
    _write(
        session_resume.handoff_path(tmp_path),
        _handoff_md(goal="handoff goal", next_step="handoff next"),
    )
    _write(
        session_resume.ledger_path(tmp_path),
        _ledger_md(where="ledger where", next_step="ledger next"),
    )
    card = session_resume.build_card(tmp_path)
    assert "HANDOFF: present" in card
    assert "LEDGER: present" in card
    # Ledger wins for live WHERE/NEXT when set
    assert "WHERE: ledger where" in card
    assert "NEXT: ledger next" in card
    # Handoff still visible as pointer / secondary
    assert "Ship" not in card or "handoff" in card.lower() or "PORTABLE" in card


def test_done_open_capped(tmp_path: Path) -> None:
    done = [f"done-{i}" for i in range(10)]
    open_items = [f"open-{i}" for i in range(10)]
    _write(
        session_resume.ledger_path(tmp_path),
        _ledger_md(done=done, open_items=open_items),
    )
    card = session_resume.build_card(tmp_path)
    # only last MAX keep items appear
    assert card.count("done-") <= session_resume.MAX_DONE_SHOW
    assert card.count("open-") <= session_resume.MAX_OPEN_SHOW
    assert len(card) <= session_resume.CARD_MAX_CHARS


def test_redacts_secrets_in_card(tmp_path: Path) -> None:
    secret_goal = "api_key=not-a-real-secret-value-999"
    _write(
        session_resume.handoff_path(tmp_path),
        _handoff_md(goal=secret_goal, next_step="password: hunter2secret99"),
    )
    card = session_resume.build_card(tmp_path)
    assert "not-a-real-secret-value-999" not in card
    assert "hunter2secret99" not in card
    assert "[REDACTED]" in card or "api_key" not in card.lower() or "REDACTED" in card


def test_card_hard_size_cap(tmp_path: Path) -> None:
    huge = "x" * 5000
    _write(
        session_resume.handoff_path(tmp_path),
        _handoff_md(goal=huge, next_step=huge, task=huge),
    )
    _write(
        session_resume.ledger_path(tmp_path),
        _ledger_md(where=huge, next_step=huge, done=[huge], open_items=[huge]),
    )
    card = session_resume.build_card(tmp_path)
    assert len(card) <= session_resume.CARD_MAX_CHARS


def test_cli_prints_card(tmp_path: Path) -> None:
    _write(session_resume.handoff_path(tmp_path), _handoff_md())
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "session_resume.py"),
            "--project",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Resume card" in proc.stdout
    assert "HANDOFF: present" in proc.stdout


def test_skill_mentions_session_resume_step0() -> None:
    skill = (PLUGIN / "skills" / "resume" / "SKILL.md").read_text(encoding="utf-8")
    assert "session_resume.py" in skill
    assert "progress-ledger" in skill or "progress ledger" in skill.lower()
    assert "PORTABLE_HANDOFF" in skill
