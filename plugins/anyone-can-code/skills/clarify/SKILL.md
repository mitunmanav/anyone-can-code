---
name: clarify
description: "Structured intake for vague or partial requests. Asks only the questions needed to remove meaningful uncertainty, then writes a local spec draft."
---

# Clarify

Use `$clarify` when the request is still too vague to plan or build safely.

## Rules

- Ask only what materially changes the build.
- Never silently assume architecture, platform, security, or behavior details.
- Prefer one question at a time.
- If the user already gave enough information, skip unnecessary intake.

## Output

Write a local draft to:

- `.codex/anyone-can-code/artifacts/SPEC-DRAFT.md`

Include:

- project goal
- target user
- platform
- top day-one features
- constraints
- known unknowns

## Escalation

- High-impact unknown: stop and ask.
- Medium-impact unknown: present ranked options and recommend one.
- Low-impact convenience detail: proceed and mark inference.
