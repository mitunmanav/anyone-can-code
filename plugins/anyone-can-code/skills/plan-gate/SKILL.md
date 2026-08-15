---
name: plan-gate
description: "Use before product file writes when no plan steps exist, or when about to code without PLAN.md. Enforce plan-then-GO. Not for pure chat or after user already approved a plan."
---

# Plan gate

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:

- talk strict caveman only
- keep answer short

Use `$plan-gate` when product code is about to be written and the plan artifact
is missing, empty, step-less, or stale.

## HARD-GATE

Do **not** write product files (app code, configs that ship, migrations) until:

1. `.codex/anyone-can-code/artifacts/PLAN.md` exists with **list steps** (bullets or numbers), and
2. User said **GO** (or clearly asked to build now).

Plan-only writes under `.codex/anyone-can-code/` are allowed without GO.

## Check (run now)

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/plan_gate.py" --repo . --json
```

Read `status`:

| status | Action |
|--------|--------|
| `ok` | Wait for GO if not given, then build via `$execute` |
| `missing` / `empty` / `no_steps` | Write or fix PLAN.md (or call `$plan`) |
| `stale` | Refresh steps for current goal |

Optional skeleton:

```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0,'<ACC_PLUGIN_ROOT>/scripts'); import plan_gate; plan_gate.write_plan_skeleton(Path('.'), goal='...', steps=['...','...'])"
```

Or write PLAN.md by hand. Tiny plan (3 lines) is fine. Skip is not free.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "I'll plan in the patch" | Plan file first. Then GO. |
| "Too small to plan" | Three bullets still. |
| "User said build — no file" | Write PLAN.md, show steps, confirm GO. |
| "State has tasks, skip PLAN.md" | Gate reads PLAN.md. Keep both aligned. |

## Soft hook (optional)

If preferences set `plan_gate_required: true`, PreToolUse may **hint** (not hard deny)
when `apply_patch` runs without a good plan. Skill still owns the workflow.

## Output

- Valid PLAN.md with goal + steps
- One short line: `Plan gate: N steps. Say GO to build.`

## Next skill

- Need tasks broken down → `$plan`
- User said GO → `$execute`
- Claiming done → `$verify`

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
