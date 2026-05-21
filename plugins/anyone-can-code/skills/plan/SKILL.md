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

Write:

- `.codex/anyone-can-code/artifacts/PLAN.md`
- `.codex/anyone-can-code/state/task-queue.md`

## Rules

- Fast path: keep the plan lean for concrete repo work.
- Full path: include scope, architecture, and verification checkpoints.
- Challenge obviously weak architecture choices before execution begins.
- Every plan item should have a verification target.
