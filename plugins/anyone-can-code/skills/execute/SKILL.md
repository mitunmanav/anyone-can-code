---
name: execute
description: "Use when a plan or concrete tasks exist and user said build/go/implement. Not to invent scope or claim done without verify."
---

# Execute

Reply rule:

- talk strict caveman only
- keep answer short

Use `$execute` when the work is planned or concrete enough to implement.

## HARD-GATE

Do **not** say "done", "works", "fixed", or "perfect" in this skill.

After meaningful progress → `$verify`. Built here = `implemented` only, never
`verified`.

Do **not** invent new product scope. Follow plan / task queue. Scope change →
update route first, then continue.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "Looks done" | Run `$verify`. No proof → not done. |
| "Tests can wait" | Verify owns proof. Hand off. |
| "Small extra feature" | Scope creep. Plan or ask. |
| "Should pass" | Not evidence. `$verify`. |

## Inputs

- `.codex/anyone-can-code/artifacts/PLAN.md`
- `.codex/anyone-can-code/state/task-queue.md`
- relevant repo files

tool_interop execute bindings: use installed skill; ACC redirect only;
PRECHECK fail → local ACC + reason.

## Rules (core)

- Extend existing code instead of rebuilding blindly.
- Update through `scripts/canonical_state.py` and claim tasks through
  `scripts/task_coordination.py` before execution.
- Loop-driven work has a loop_budget. After loop_budget iterations: STOP. Show real-use proof or ask user.
- Risky ship/delete/remote: `scripts/safety_receipts.py` first.
- If `patch_retry` present and a failed patch occurs: reread exact target before retry.
- If `mechanics_docs_gate` marks platform mechanics work, do not edit code
  until the docs brief exists (platform mechanics).
- Plain words only. No jargon. Warm, not a robot.
- Full rule list: `references/execute-details.md`.

## Narration / walkthrough (always on)

- Narrate each build step in plain lines. No code shown unless user asks.
- Step fails: one plain line — what broke + next try.
- Long work: `scripts/walkaway_pack.py --goal`, then native `/goal`.

## Output

- code changes + updated workflow state + notes under `.codex/anyone-can-code/artifacts/`

## Evidence rules

- Do not hardcode test counts in docs. Say "all tests green"; let CI show the number.

## Worktree for risky work

Big refactor: tell user Worktree mode (safe copy; Handoff merges). Git only;
no Git → local with care.

## Next skill

Next: `$verify` before any done claim. On fail → `$fix`.

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
