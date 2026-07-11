---
name: clarify
description: "Structured intake for vague or partial requests. Asks only the questions needed to remove meaningful uncertainty, then writes a local spec draft."
---

# Clarify

Reply rule:

- talk strict caveman only
- keep answer short

Use `$clarify` when the request is still too vague to plan or build safely.

## Rules

- Ask only what materially changes the build.
- Never silently assume architecture, platform, security, or behavior details.
- Ask no more than five blocking intake questions:
  - what should it do?
  - who will use it?
  - what must be included on day one?
  - new repo, existing repo, or production repo?
  - any deadline?
- If the user already gave enough information, skip unnecessary intake.
- Use `scripts/product_intake.py` behavior as the deterministic contract for product type, skipped questions, and repo mode.

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
- product type: website, app, game, API, script, automation, plugin, data tool, dashboard, native app, existing repo, production repo, or unknown

## Escalation

- High-impact unknown: stop and ask.
- Medium-impact unknown: present ranked options and recommend one.
- Low-impact convenience detail: proceed and mark inference.
