---
name: fix
description: "Use when verify failed, same error twice, or something is broken. Diagnose before retry; not for first green build."
---

# Fix

Reply rule:

- talk strict caveman only
- keep answer short

Use `$fix` when verification keeps failing or the current route needs controlled recovery.

## Inputs

- `.codex/anyone-can-code/state/turn-ledger.jsonl`
- `.codex/anyone-can-code/artifacts/VERIFICATION.md`
- `.codex/anyone-can-code/artifacts/resume-note.md`

## Rules

- Never silently continue after repeated failure.
- Prefer repair guidance before revert-like behavior.
- If user work may overlap with plugin-made changes, pause and surface the conflict.
- Record the recovery outcome in the local artifacts area.

## Next skill

Next: `$execute` for the repair, then `$verify` again.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
