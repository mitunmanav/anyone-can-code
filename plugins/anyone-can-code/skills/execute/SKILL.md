---
name: execute
description: "Builds from the current task queue, follows the chosen route, and updates local workflow state without pretending unverified work is finished."
---

# Execute

Use `$execute` when the work is planned or concrete enough to implement.

## Inputs

- `.codex/anyone-can-code/artifacts/PLAN.md`
- `.codex/anyone-can-code/state/task-queue.md`
- relevant repo files

## Rules

- Extend existing code instead of rebuilding blindly.
- Keep route changes visible.
- Do not claim success until `$verify` or equivalent evidence exists.
- Update workflow state after meaningful progress.
- Update through `scripts/canonical_state.py`; derived files are not separate
  writable truths.
- Use only: `in scope`, `designed`, `approved`, `implemented`, `verified`,
  `blocked`, `deferred`.
- Code written but not checked is `implemented`, never `verified`.
- Record route, next step, evidence, failures, silent failures, unverified work,
  and uncertainty in workflow state.
- A mid-work requirement change updates route and next step before execution
  resumes.
- Scope change preserves old state in history, marks affected verification
  stale, updates every derived view, and moves active cursor to new work.

## Output

- code changes
- updated workflow state
- optional notes under `.codex/anyone-can-code/artifacts/`
