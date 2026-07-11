---
name: govern
description: "Controls meaningful scope changes by comparing the draft change against the current local plan, verification state, and active workflow route."
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

## Worktree for scope jumps

Approved scope change that rewrites large parts: suggest Worktree mode — a
safe copy, real project untouched until the change proves itself.
