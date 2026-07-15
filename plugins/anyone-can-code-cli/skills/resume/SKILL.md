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

Run `python "$PLUGIN_ROOT/scripts/runtime_info.py" --resolve-project "."`
first. Use returned `project_root`. If result is `ambiguous`, block recovery
and show candidates; never merge or replace competing state automatically.

Start with canonical
`.codex/anyone-can-code/state/workflow.json`. Confirm derived files carry same
transaction ID. Use history, ledgers, artifacts, and `AGENTS.md` only as
supporting evidence.

Use `scripts/canonical_state.py` recovery behavior to re-anchor from canonical
state. Read `active_task_capsule` for goal, task, decisions, boundaries,
evidence, and next action. Before known restart, handoff, or compaction risk,
save a context-transition capsule when possible.
If `usage_checkpoint` or session evidence says primary usage is at least 85%,
checkpoint before continuing. At 90%, split before more work. At 94%, stop now
unless the user explicitly chooses to continue.
Ignore legacy workflow truth fields if present. Resume from canonical
verification, transaction, capsule, recovery, and next-action fields only.

Choose the lightest recovery mode that is still safe.
If active truths conflict, block work and repair state before resuming.
Report every missing or uncertain field. Never invent recovery context.
Hooks may help with session context, but resume must work when hooks are absent,
failed, or circuit-broken. Do not treat hook output as canonical truth.

## Past questions

"What did we decide about X?" — do not shrug. Run
`python "$PLUGIN_ROOT/scripts/past_answer.py" "<keywords>"` and answer with
the date of each record. Nothing found: say "no record" honestly.
