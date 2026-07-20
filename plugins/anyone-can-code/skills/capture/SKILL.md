---
name: capture
description: "Use when user wants an explicit recorded decision or blocker saved to artifacts. Not silent monitoring."
---

# Capture

Reply rule:

- talk strict caveman only
- keep answer short

Use `$capture` when you want to persist an important decision or blocker.

## Output

Append a structured entry to:

- `.codex/anyone-can-code/artifacts/decisions.md`

Include:

- decision or blocker
- reason
- context
- who confirmed it

## Rule

This is not a silent prompt monitor. It is an explicit recording step.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
