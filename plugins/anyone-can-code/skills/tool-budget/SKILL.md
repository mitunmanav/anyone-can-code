---
name: tool-budget
description: "Use when user or agent wants tool-call budget, soft stop after many tools, Cascade-style continue. Not for token $usage."
---

# Tool budget

Cascade-style **soft** tool-call budget (default **20** per segment). Soft warn only — never hard deny.

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

## File

`.codex/anyone-can-code/state/tool-budget.json`

## Commands

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." init --limit 20
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." status
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." --json status
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." set-limit 30
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." continue
python3 "<ACC_PLUGIN_ROOT>/scripts/tool_budget.py" --project "." reset
```

## When over / soft warn

1. Stop thrash. Summarize WHERE + NEXT.
2. Ask user: continue segment? change limit? stop?
3. On yes continue → run `continue` (new segment, count 0).
4. Prefer plan + fewer tools next segment.

## Auto track (optional)

Clean `PostToolUse` (Bash|apply_patch success) may increment via audit when prefs `tool_budget_track` is not false (default on). Soft `additionalContext` only — no deny.

Opt out: prefs `tool_budget_track: false`.

## Rules

- Soft only. Never claim hard block.
- `$usage` = tokens. This skill = tool **count**.
- Explicit `$tool-budget` — do not auto-fire the skill body every turn.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
