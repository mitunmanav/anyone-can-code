"""Write scoreboard.md and PROOF.md."""
from __future__ import annotations

from pathlib import Path


def scoreboard_markdown(scoreboard: dict[str, dict[str, str]]) -> str:
    lines = [
        "# ACC CLI blind scoreboard",
        "",
        "| row | kind | status | evidence | notes |",
        "|-----|------|--------|----------|-------|",
    ]
    for name, row in scoreboard.items():
        ev = (row.get("evidence") or "").replace("|", "\\|").replace("\n", " ")
        notes = (row.get("notes") or "").replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {name} | {row.get('kind', '')} | {row.get('status', '')} | {ev} | {notes} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_scoreboard(out_dir: Path, scoreboard: dict[str, dict[str, str]]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "scoreboard.md"
    path.write_text(scoreboard_markdown(scoreboard), encoding="utf-8")
    return path


def write_proof(
    *,
    out_dir: Path,
    run_id: str,
    overall: str,
    env: dict,
    scoreboard: dict[str, dict[str, str]],
    core_notes: str,
    bias_notes: list[str] | None = None,
    not_proven_why: list[str] | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    bias_notes = bias_notes or []
    not_proven_why = not_proven_why or []
    lines = [
        f"# ACC CLI Blind Proof — {run_id}",
        "",
        f"- **Overall:** {overall}",
        f"- **Model:** {env.get('model', '?')}",
        f"- **Reasoning:** {env.get('model_reasoning_effort', '?')}",
        f"- **Codex home:** {env.get('codex_home', '?')}",
        f"- **Sandbox:** {env.get('sandbox', '?')}",
        f"- **Bypass hook trust:** {env.get('bypass_hook_trust', '?')}",
        f"- **Bypass approvals:** {env.get('bypass_approvals', '?')}",
        f"- **ACC / plugin note:** {env.get('plugin_note', 'see installed cache')}",
        f"- **Codex version:** {env.get('codex_version', '?')}",
        "",
        "## Core product",
        "",
        core_notes or "(none)",
        "",
        "## Bias / honesty notes",
        "",
    ]
    if bias_notes:
        lines.extend(f"- {b}" for b in bias_notes)
    else:
        lines.append("- (none)")
    lines.extend(["", "## NOT PROVEN / FAIL notes", ""])
    if not_proven_why:
        lines.extend(f"- {x}" for x in not_proven_why)
    else:
        lines.append("- (see scoreboard)")
    lines.extend(["", "## Matrix", "", scoreboard_markdown(scoreboard)])
    path = out_dir / "PROOF.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
