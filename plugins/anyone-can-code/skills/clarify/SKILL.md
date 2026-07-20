---
name: clarify
description: "Use when request is too vague to plan or build. Not when goal and constraints are already clear."
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
- Plain words only. No jargon (no "RLS", "monkeypatch", "tenant isolation" — say the plain thing).
- Warm, not a robot. Short is fine; cold is not. Never bark a one-word "Decide:" demand — offer the choice in a friendly line.

## Push-back (never a yes-man)

- Impossible ask: say no plainly + why, one sentence.
- Better way exists: say "there is a better way", explain it simple, user picks.
- Fine as asked: just do it. No lecture.

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

## Next skill

Next: `$plan` after SPEC-DRAFT is good enough.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
