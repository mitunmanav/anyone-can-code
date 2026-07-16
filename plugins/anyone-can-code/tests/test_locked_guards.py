"""Beta.4 locked-rule guards (T5 + T6).

Two standing product rules, enforced forever by CI:
- ACC house body budget: every SKILL.md stays at or under 4000 characters
  (ACC caveman rule — NOT the Codex skills-list budget). Codex docs cap the
  initial skills *list* (names + descriptions) at 2% of context or 8,000
  chars when unknown. Hook turn context keeps a separate small cap.
- Codex-native only: plugin Python needs nothing outside the standard
  library, so no user ever runs a dependency install.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]

SKILL_CHAR_BUDGET = 4000

# Python code shipped to end users (tests stay out: they may use pytest).
SHIPPED_CODE_DIRS = ("scripts", "hooks", "mcp")


def shipped_python_files():
    files = []
    for name in SHIPPED_CODE_DIRS:
        root = PLUGIN / name
        if root.is_dir():
            files.extend(sorted(root.rglob("*.py")))
    return files


def test_every_skill_fits_caveman_budget():
    skills = sorted(PLUGIN.glob("skills/*/SKILL.md"))
    assert skills, "no skills found — wrong plugin layout?"
    over = {
        str(p.relative_to(PLUGIN)): len(p.read_text(encoding="utf-8"))
        for p in skills
        if len(p.read_text(encoding="utf-8")) > SKILL_CHAR_BUDGET
    }
    assert not over, f"skills over {SKILL_CHAR_BUDGET} chars: {over}"


def test_hook_context_cap_stays_caveman():
    hooks_scripts = PLUGIN / "hooks" / "scripts"
    sys.path.insert(0, str(hooks_scripts))
    try:
        import guard
    finally:
        sys.path.remove(str(hooks_scripts))
    assert guard.MAX_TURN_CONTEXT_CHARS <= SKILL_CHAR_BUDGET


def test_shipped_python_is_stdlib_only():
    files = shipped_python_files()
    assert files, "no shipped python found — wrong plugin layout?"

    # Local modules may import each other by bare name.
    local = {p.stem for p in files}
    local.update(p.name for p in PLUGIN.iterdir() if p.is_dir())

    offenders = {}
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            else:
                continue
            for name in names:
                if name in sys.stdlib_module_names or name in local:
                    continue
                offenders.setdefault(str(path.relative_to(PLUGIN)), []).append(name)
    assert not offenders, f"non-stdlib imports in shipped code: {offenders}"
