---
name: govern
description: "Use when a change would alter accepted scope/plan and needs user confirm. Not for tiny in-scope edits."
---

# Govern

Reply rule:

- talk strict caveman only
- keep answer short

Use `$govern` when a proposed change could materially alter the accepted scope.

## Inputs

- `.codex/anyone-can-code/state/workflow.json`
- `.codex/anyone-can-code/artifacts/SPEC-DRAFT.md`
- `.codex/anyone-can-code/artifacts/PLAN.md`
- `.codex/anyone-can-code/state/task-queue.md`

## Rules

- Surface consequences before changing direction.
- Require explicit user confirmation for meaningful scope changes.
- Keep a timestamped change record in local artifacts.
- Update through `scripts/canonical_state.py`; plans and task queues are
  derived views, not separate truth.
- Risky, remote, destructive, install, publish, or release changes must also
  pass the safety receipt gate before execution.
- Never claim a Git, GitHub, rollback, publish, release, or remote action
  happened unless receipt and evidence prove it.

## Push-back (never a yes-man)

- Impossible ask: say no plainly + why, one sentence.
- Better way exists: say "there is a better way", explain it simple, user picks.
- Fine as asked: just do it. No lecture.

## Worktree for scope jumps

Approved scope change that rewrites large parts: suggest Worktree mode — a
safe copy, real project untouched until the change proves itself.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
