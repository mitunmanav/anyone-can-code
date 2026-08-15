---
name: checkpoint
description: "Use when user wants save/list/restore file checkpoints, or says $checkpoint. Explicit only. Pattern snapshot (list+hash+blobs), not Cline shadow-git, not auto."
---

# Checkpoint

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$checkpoint` to **save**, **list**, or **restore** project file snapshots.
Explicit skill — do not auto-fire. Never touch real `.git` history.

## Pattern (not a clone)

Inspired by Cline shadow-git idea: roll back files without dirtying user Git.
ACC stores **file list + sha256 + content blobs** under:

`.codex/anyone-can-code/state/checkpoints/<id>/`

Not a second git repo. No rename of `.git`. No hooks auto-commit.

## Commands

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/checkpoints.py" --project "." save --label "before-risky"
python3 "<ACC_PLUGIN_ROOT>/scripts/checkpoints.py" --project "." list
python3 "<ACC_PLUGIN_ROOT>/scripts/checkpoints.py" --project "." restore <id>
# JSON:
python3 "<ACC_PLUGIN_ROOT>/scripts/checkpoints.py" --project "." save --label "x" --json
```

## Steps

1. **Save** before risky edits or when user asks.
2. **List** → pick an `id` (`cp-...`).
3. **Restore** only with user YES on that id (rewinds stored files; does not delete newer extra files).
4. Report short card:

```
WHERE: checkpoint
ACTION: save|list|restore
ID: …
FILES: N
NEXT: keep building or $verify
```

## Rules

- Explicit only. No silent restore.
- Restore = files with stored blobs. Huge/skipped files stay as-is.
- Ignore noise: `.git`, `node_modules`, `.codex`, venvs, caches.
- User Git commits stay theirs. This is local ACC state only.
- Windows: `python` from repo root; no Bash-only glue.

## Next skill

After restore → `$verify` if product code changed. Optional `$status`.

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
