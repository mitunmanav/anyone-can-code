---
name: auto-lint
description: "Use after code edits to detect and run project lint/test tools (pytest, ruff, eslint). Explicit only; not for pure plan chat."
---

# Auto lint

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$auto-lint` after edits (or when pref `auto_lint=true` soft-hints).
Mirrors Aider auto-lint/auto-test: check what the edit broke, then fix.

## Docs

- Aider lint/test after edit (auto-lint / auto-test).
- Codex PostToolUse can inject soft `additionalContext` (not a block).
- Superpowers: TDD + verify before "done".

## Steps

1. **Detect** (no write):
   `python3 "<ACC_PLUGIN_ROOT>/scripts/auto_lint.py" --json --root .`
2. **0 tools** → say none found. Stop. Optional: ask user for lint/test cmd.
3. **Run each** command from detect (repo root). Capture exit + short tail.
4. **Report card:**

```
WHERE: auto-lint
TOOLS: …
PASS/FAIL: per tool
FIX: short next (or green)
```

5. Fail → fix with `$fix` / edit → re-run failed tools. Never claim done on red.
6. Green → optional `$verify`.

## Pref (optional soft hook)

`preferences.json` key `auto_lint: true` → PostToolUse soft hint after
edit tools only. Default **off**. Soft context only — never deny / never
break fail-closed gates.

## Rules

- Detect only tools **present** (config or layout). No invent.
- Explicit skill — do not auto-fire whole skill without user/`$auto-lint`.
- Windows: `python` / `npx` from repo root; no Bash-only glue.
- Hint ≠ run. You still must **run** commands for evidence.

## Next skill

Fail → `$fix` then re-run. Pass → `$verify` if claiming done.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
