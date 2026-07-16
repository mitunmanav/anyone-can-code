---
name: plan
description: "Turns the accepted spec or concrete request into an executable local plan with ordered tasks, dependencies, and verification targets."
---

# Plan

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:

- talk strict caveman only
- keep answer short

Use `$plan` after the request is clear enough to break into real work.

## Inputs

- `.codex/anyone-can-code/artifacts/SPEC-DRAFT.md`, or
- a concrete repo-scoped feature / repair request

## Output

Update canonical state through `scripts/canonical_state.py` with plan, active
task, boundaries, and next action. Create or replace concrete task queues
through `scripts/task_coordination.py` so each task has name, dependencies,
owner, status, claim fields, and evidence. Derived plan guidance and task queue
must share the same transaction ID.

## External tool interop (Superpowers-style)

If front door `tool_interop` has an available `writing-plans` binding for phase
`plan`, you may invoke that installed skill for micro-steps — but write the
durable plan only to the binding `redirect.write_to` (ACC `PLAN.md`), never to
foreign defaults like `docs/superpowers/plans/`. ACC stays workflow owner.
Missing PRECHECK → local ACC plan only, say why.

Show one concise builder-facing line, for example:
  - `Plan: website + auth + deploy. Payments later.`

For product-intake plans, generate the adapted checklist through `scripts/product_intake.py` and include only relevant areas. Each checklist item uses:

- `decision`: include, defer, skip, or unknown
- `state`: in scope, designed, approved, implemented, verified, blocked, deferred

## Domain routing

After generating the engineering checklist, route included domains to execution instructions:

1. Call `python3 "<ACC_PLUGIN_ROOT>/scripts/domain_router.py" --checklist <path>` or invoke `route_domains(checklist, product_type)` directly.
2. Each returned domain has `instructions` — use them when building that area.
3. All UX domains (theme, responsive, accessibility, loading states, error states) are automatically included for web/app/dashboard products.
4. Never skip a domain marked `include` without recording it as `deferred` in canonical state with reason.

## Parallel research (say it literally)

When the plan needs reading in several places at once (big repo, many
domains), instruct Codex in plain words — it never spawns on a hint:

```
Spawn a subagent.
Job: <one exact research task, e.g. "map every route in src/api">
Scope: <exact files/dirs, read-only>
Expected output: <exact shape, e.g. "bullet list, max 10 lines, file:line refs">
Speak caveman style: simple, short, direct, step by step, clear YES/NO recommendations, no ceremony.
```

- One job per agent. Max 3 in parallel.
- Every agent result returns to ACC and gets checked before it enters the plan.

## Rules

- Fast path: keep the plan lean for concrete repo work.
- Full path: include scope, architecture, and verification checkpoints.
- Challenge obviously weak architecture choices before execution begins.
- Every plan item should have a verification target.
- Every executable task should have dependencies, owner, status, and evidence target.
- If `mechanics_docs_gate` marks platform mechanics work, add a docs brief
  task before implementation. The docs brief must cite official docs/source or
  record controlled proof plus uncertainty before platform mechanics code.
- Never write a separate task queue that disagrees with canonical state.
- Hide low-level tooling from builder-facing plan lines unless the user asks for technical detail.
