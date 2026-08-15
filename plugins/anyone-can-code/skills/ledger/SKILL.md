---
name: ledger
description: "Use when user wants a progress ledger, fight context rot, or says $ledger / $context-rot / where-next-done-open. Not for deep rebuilds."
---

# Ledger (context rot)

Use `$ledger` (alias idea: `$context-rot`) to keep a small on-disk progress board.

Reply rule:

- talk strict caveman only
- keep answer short

Script root: use `ACC_PLUGIN_ROOT` from SessionStart context (hooks inject it).
`PLUGIN_ROOT` is hooks-only — do not assume it in the agent shell.

## File

`.codex/anyone-can-code/state/progress-ledger.md`

Sections: **WHERE** / **NEXT** / **DONE** / **OPEN** (+ optional NOTES for capsule pointers).

## Commands

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." init --where "what we are doing" --next "immediate next"
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." where "updated where"
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." next "updated next"
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." done "finished item"
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." open "still open item"
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." show
python3 "<ACC_PLUGIN_ROOT>/scripts/context_rot.py" --project "." inject
```

## Rules

1. Init once per project (or when work starts).
2. Update NEXT every meaningful step. Mark DONE when done.
3. Do not paste the whole ledger into chat every turn — point at the file.
4. SessionStart injects a **thin one-liner** only if the file exists (opt-out: prefs `progress_ledger_inject=false`).
5. PreCompact / Stop append capsule pointers into NOTES when ledger already exists — they do not create the file.

## When to use

- long multi-step work
- after compact risk / resume
- user asks "where are we" and wants a durable board (also still use `$status` / `$resume`)

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
