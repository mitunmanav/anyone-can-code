#!/usr/bin/env python3
"""ACC CLI blind proof runner (stdlib)."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.capture import (  # noqa: E402
    list_acc_files,
    memory_note_files,
    parse_hooks,
    parse_skill_reads,
)
from lib.matrix import empty_scoreboard  # noqa: E402
from lib.proof_write import write_proof, write_scoreboard  # noqa: E402
from lib.runner import init_project, run_codex_exec  # noqa: E402
from lib.scenarios import assert_no_coaching, load_pack, load_scenarios  # noqa: E402
from lib.score import apply_doctor, apply_session_evidence, overall_result  # noqa: E402


def _codex_version() -> str:
    try:
        p = subprocess.run(
            ["codex", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return (p.stdout or p.stderr or "").strip().splitlines()[0][:120]
    except Exception as exc:  # noqa: BLE001
        return f"unknown ({exc})"


def _detect_core(project: Path) -> tuple[bool, str]:
    py_files = list(project.glob("*.py")) + list(project.glob("**/*.py"))
    py_files = [p for p in py_files if ".codex" not in p.parts and ".git" not in p.parts]
    tests = list(project.glob("tests/**/*.py")) + list(project.glob("test_*.py"))
    readme = project / "README.md"
    notes = []
    if py_files:
        notes.append(f"python files: {', '.join(str(p.relative_to(project)) for p in py_files[:8])}")
    if tests:
        notes.append(f"tests: {len(tests)}")
    if readme.exists() and "habit" in readme.read_text(encoding="utf-8", errors="replace").lower():
        notes.append("README mentions habit")
    # Try pytest if tests exist
    test_ok = None
    if tests:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=no"],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        test_ok = proc.returncode == 0
        notes.append(f"pytest exit={proc.returncode}")
        if proc.stdout:
            notes.append(proc.stdout.strip()[:200])
    core_ok = bool(py_files) and (test_ok is True or (not tests and readme.exists()))
    if not py_files:
        core_ok = False
        notes.append("no app python files found")
    return core_ok, "; ".join(notes) if notes else "no core signals"


def _hopes_met(sb: dict, hopes: list[str]) -> bool:
    for h in hopes or []:
        row = sb.get(h) or sb.get(h.lower())
        if not row or row.get("status") == "NOT PROVEN":
            return False
    return True


def _run_doctor(project: Path) -> dict | None:
    # Prefer installed plugin doctor
    candidates = [
        Path.home()
        / ".codex/plugins/cache/anyone-can-code-marketplace/anyone-can-code",
    ]
    doctor = None
    for base in candidates:
        if not base.is_dir():
            continue
        vers = sorted(base.iterdir(), reverse=True)
        for v in vers:
            d = v / "scripts" / "doctor.py"
            if d.is_file():
                doctor = d
                break
        if doctor:
            break
    if doctor is None:
        return None
    proc = subprocess.run(
        [sys.executable, str(doctor), "--json"],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    try:
        data = json.loads(proc.stdout or "{}")
        return data.get("summary") or {}
    except json.JSONDecodeError:
        return None


def dry_parse() -> int:
    pack_path = ROOT / "scenarios.json"
    items = load_scenarios(pack_path)
    assert_no_coaching(items)
    sb = empty_scoreboard()
    print(f"scenarios: {len(items)} ({', '.join(i['id'] for i in items)})")
    print(f"matrix rows: {len(sb)}")
    print("coaching: OK (none found)")
    pack = load_pack(pack_path)
    print(f"model: {pack.get('model')} effort: {pack.get('model_reasoning_effort')}")
    return 0


def run_pack(
    *,
    run_id: str,
    only: list[str] | None,
    codex_home: Path | None,
    max_retries: int | None,
) -> int:
    pack = load_pack(ROOT / "scenarios.json")
    items = load_scenarios(ROOT / "scenarios.json")
    assert_no_coaching(items)
    if only:
        want = set(only)
        items = [i for i in items if i["id"] in want]
    model = pack.get("model") or "gpt-5.4-mini"
    effort = pack.get("model_reasoning_effort") or "low"
    retries_max = max_retries if max_retries is not None else int(pack.get("max_retries") or 2)

    art = ROOT / "artifacts" / run_id
    if art.exists():
        shutil.rmtree(art)
    project = art / "project"
    sessions = art / "sessions"
    sessions.mkdir(parents=True)
    init_project(project)

    sb = empty_scoreboard()
    bias = [
        "Strict blind prompts from scenarios.json (no $skill names).",
        "Sandbox danger-full-access + bypass flags recorded for automation.",
    ]
    if codex_home:
        bias.append(f"Isolated CODEX_HOME={codex_home}")
    not_proven_why: list[str] = []
    last_env: dict = {
        "model": model,
        "model_reasoning_effort": effort,
        "codex_version": _codex_version(),
    }

    for sc in items:
        sid = sc["id"]
        hopes = sc.get("hopes") or []
        prompts = [sc["prompt"]] + list(sc.get("retries") or [])
        prompts = prompts[: 1 + retries_max]
        safety_mode = bool(sc.get("fail_if_executed")) or sid == "S7"

        for attempt, prompt in enumerate(prompts):
            notes_before = {str(p) for p in memory_note_files(project)}
            code, out, err, env_notes = run_codex_exec(
                project=project,
                prompt=prompt,
                model=model,
                effort=effort,
                codex_home=codex_home,
            )
            last_env.update(env_notes)
            last_env["codex_version"] = _codex_version()

            tag = f"{sid}_a{attempt}"
            (sessions / f"{tag}.out").write_text(out, encoding="utf-8")
            (sessions / f"{tag}.err").write_text(err, encoding="utf-8")
            (sessions / f"{tag}.meta.json").write_text(
                json.dumps({"exit": code, "env": env_notes}, indent=2),
                encoding="utf-8",
            )

            hooks = parse_hooks(err)
            skills = parse_skill_reads(err)
            acc_files = list_acc_files(project)
            apply_session_evidence(
                sb,
                hooks=hooks,
                skills=skills,
                acc_files=acc_files,
                stdout=out,
                stderr=err,
                scenario_id=sid,
                project=project,
                safety_mode=safety_mode,
                notes_before=notes_before,
            )
            print(f"{tag} exit={code} hooks={sorted(hooks)} skills={sorted(skills)}")

            if _hopes_met(sb, hopes) or attempt == len(prompts) - 1:
                if not _hopes_met(sb, hopes):
                    missing = [
                        h
                        for h in hopes
                        if (sb.get(h) or sb.get(str(h).lower()) or {}).get("status")
                        == "NOT PROVEN"
                    ]
                    not_proven_why.append(
                        f"{sid}: hopes still NOT PROVEN after {attempt + 1} try(s): {missing}"
                    )
                break

    summary = _run_doctor(project)
    if summary is not None:
        apply_doctor(sb, summary)
    else:
        not_proven_why.append("doctor: script not found or non-JSON")

    core_ok, core_notes = _detect_core(project)
    overall = overall_result(sb, core_ok=core_ok)
    write_scoreboard(art, sb)
    write_proof(
        out_dir=art,
        run_id=run_id,
        overall=overall,
        env=last_env,
        scoreboard=sb,
        core_notes=core_notes,
        bias_notes=bias,
        not_proven_why=not_proven_why,
    )
    print(f"overall={overall}")
    print(f"artifacts={art}")
    print(f"PROOF={art / 'PROOF.md'}")
    return 0 if overall == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="ACC CLI blind proof runner")
    p.add_argument("--dry-parse", action="store_true", help="load scenarios only")
    p.add_argument("--run-id", default="", help="artifact folder name")
    p.add_argument(
        "--scenarios",
        default="",
        help="comma list e.g. S1,S2 (default all)",
    )
    p.add_argument(
        "--codex-home",
        default="",
        help="optional isolated CODEX_HOME (disclose in PROOF)",
    )
    p.add_argument("--max-retries", type=int, default=None)
    args = p.parse_args(argv)

    if args.dry_parse:
        return dry_parse()
    if not args.run_id:
        p.error("--run-id required unless --dry-parse")
    only = [x.strip() for x in args.scenarios.split(",") if x.strip()] or None
    home = Path(args.codex_home) if args.codex_home else None
    return run_pack(
        run_id=args.run_id,
        only=only,
        codex_home=home,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    raise SystemExit(main())
