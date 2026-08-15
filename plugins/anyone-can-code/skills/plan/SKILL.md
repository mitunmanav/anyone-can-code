---
name: plan
description: "Use when goal/spec is clear and you need ordered tasks before writing code. Not while still clarifying."
---

# Plan

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:

- talk strict caveman only
- keep answer short

Use `$plan` after the request is clear enough to break into real work.

## HARD-GATE

Do **not** write product code, scaffold, or run `$execute` until:

1. This skill wrote/updated the plan (canonical state + task queue), and
2. User said go (or clearly asked to build next).

"Too simple to plan" is still a short plan. Plan can be three lines. Skip is not free.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "I'll just start coding" | Plan first. Then user go. |
| "Too small for a plan" | Tiny plan still. |
| "User said build — skip plan" | If no tasks exist, plan first or ask one clarifying line. |
| "I'll plan while coding" | No. Plan ends before build. |

## Inputs

- `.codex/anyone-can-code/artifacts/SPEC-DRAFT.md`, or
- a concrete repo-scoped feature / repair request

## Output

Update canonical state through `scripts/canonical_state.py` with plan, active
task, boundaries, and next action. Create or replace concrete task queues
through `scripts/task_coordination.py` so each task has name, dependencies,
owner, status, claim fields, and evidence. Derived plan guidance and task queue
must share the same transaction ID.

Also write `.codex/anyone-can-code/artifacts/PLAN.md` with **list steps**
(bullets or numbers). `$plan-gate` and product writes expect this file.

Show one concise builder-facing line, for example:

- `Plan: website + auth + deploy. Payments later.`

More detail (domain routing, product-intake, tool_interop): read
`references/plan-details.md` when needed.

## Parallel research (say it literally)

When plan needs multi-place research, instruct Codex in plain words:

```
Spawn a subagent.
Job: <one exact research task>
Scope: <exact files/dirs, read-only>
Expected output: <exact shape>
Speak caveman style: simple, short, direct, step by step, clear YES/NO recommendations, no ceremony.
```

- One job per agent. Max 3 in parallel.
- Every agent result returns to ACC and gets checked before it enters the plan.

## Core rules

- Every plan item should have a verification target.
- Never write a separate task queue that disagrees with canonical state.
- If `mechanics_docs_gate` marks platform mechanics work, add a docs brief
  task before implementation (platform mechanics + docs brief required).
- Hide low-level tooling from builder-facing plan lines unless user asks.

## Next skill

Next: `$execute` when user says go. Do not build during plan.

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
