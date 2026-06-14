---
name: resume
description: "Resumes, reconstructs, repairs, or abandons stale workflow state using the local project artifacts."
---

# Resume

Use `$resume` when a session was interrupted or the state looks stale.

Reply rule:

- talk strict caveman only
- keep answer short
- choose light fix first

## Recovery modes

- `resume`: continue from intact state
- `reconstruct`: rebuild state from artifacts
- `repair`: fix stale or corrupt workflow state
- `abandon`: start a fresh run while preserving artifacts

## Read from

Start with canonical
`.codex/anyone-can-code/state/workflow.json`. Confirm derived files carry same
transaction ID. Use history, ledgers, artifacts, and `AGENTS.md` only as
supporting evidence.

Use `scripts/canonical_state.py` recovery behavior to re-anchor from canonical
state. Read `active_task_capsule` for goal, task, decisions, boundaries,
evidence, and next action. Before known restart, handoff, or compaction risk,
save a context-transition capsule when possible.

Choose the lightest recovery mode that is still safe.
If active truths conflict, block work and repair state before resuming.
Report every missing or uncertain field. Never invent recovery context.
Hooks may help with session context, but resume must work when hooks are absent,
failed, or circuit-broken. Do not treat hook output as canonical truth.
