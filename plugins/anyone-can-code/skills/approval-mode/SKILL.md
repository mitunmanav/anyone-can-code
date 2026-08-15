---
name: approval-mode
description: "Use when user sets ACC approval grade (off|ask|allowlist|strict) or runs $approval-mode. Explicit only. Not Codex host /permissions."
---

# Approval mode

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$approval-mode` to show or set ACC **approval grade**.

## Grades (ACC prefs only)

| Grade | ACC soft behavior |
|-------|-------------------|
| `off` | ACC never auto-allows. Host Codex prompts only. |
| `ask` | Default. Safe reads + safe test/status shell may auto-allow. Rest asks. |
| `allowlist` | Safe reads + shell matching `approval_allowlist` only. |
| `strict` | ACC never auto-allows. Extra caution. Good for production care. |

Storage: `.codex/anyone-can-code/settings/preferences.json` keys `approval_mode`, `approval_allowlist`.

## Job

1. Show current:

```
python3 "<ACC_PLUGIN_ROOT>/scripts/approval_grades.py" --project-root "." --json
```

2. Set grade (user said which):

```
python3 "<ACC_PLUGIN_ROOT>/scripts/approval_grades.py" --project-root "." --set ask --json
```

Allowlist grade + list:

```
python3 "<ACC_PLUGIN_ROOT>/scripts/approval_grades.py" --project-root "." --set allowlist --allowlist "git status" "python -m pytest" --json
```

3. Say plain: what changed + that **Codex host** sandbox/approvals stay separate (`/permissions`). ACC does not set Codex APIs.

## Hard rules

- Explicit skill only — do not auto-fire every turn.
- Do not invent Codex flags or rewrite `config.toml`.
- Hard guard denials still block in every grade.
- Prefer `ask` for day work; `strict` when user says production/careful.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
