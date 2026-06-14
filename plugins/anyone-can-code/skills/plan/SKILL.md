---
name: plan
description: "Turns the accepted spec or concrete request into an executable local plan with ordered tasks, dependencies, and verification targets."
---

# Plan

Use `$plan` after the request is clear enough to break into real work.

## Inputs

- `.codex/anyone-can-code/artifacts/SPEC-DRAFT.md`, or
- a concrete repo-scoped feature / repair request

## Output

Update canonical state through `scripts/canonical_state.py` with plan, tasks,
active task, boundaries, and next action. Derived plan guidance and task queue
must share the same transaction ID.

Show one concise builder-facing line, for example:
  - `Plan: website + auth + deploy. Payments later.`

For product-intake plans, generate the adapted checklist through `scripts/product_intake.py` and include only relevant areas. Each checklist item uses:

- `decision`: include, defer, skip, or unknown
- `state`: in scope, designed, approved, implemented, verified, blocked, deferred

## Rules

- Fast path: keep the plan lean for concrete repo work.
- Full path: include scope, architecture, and verification checkpoints.
- Challenge obviously weak architecture choices before execution begins.
- Every plan item should have a verification target.
- Never write a separate task queue that disagrees with canonical state.
- Hide low-level tooling from builder-facing plan lines unless the user asks for technical detail.
