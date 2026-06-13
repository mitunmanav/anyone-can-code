---
name: onboard
description: "Detects whether the user is starting from an idea, a spec, an existing repo, or a bug. Builds the initial local workflow context without forcing unnecessary steps."
---

# Onboard

Use `$onboard` when the plugin needs to understand the starting point before planning or building.

## Entry modes

- `idea`: a vague or partial idea, likely routes to `$clarify`.
- `written-spec`: requirements already exist, likely routes to `$plan`.
- `existing-repo`: repo scan first, then route into fast path or full path.
- `feature-request`: concrete change in an existing codebase, usually fast path.
- `bug-fix`: bug or failure, route into repair and verification.
- `polish-review`: optimization or review pass.
- `ship-verify`: closing and verification path.
- `requirement-change`: update plan/state, then resume from the last valid step.

## Output

- Updates `.codex/anyone-can-code/state/workflow.json`
- Writes or refreshes `AGENTS.md`
- Chooses a visible route instead of silently jumping phases

## Rule

Do not ask broad setup questions if the repo and the user request already answer them.
Use `scripts/front_door.py` as the shared classifier. Do not create a second
entry-mode classifier in this skill.

Memory onboarding shows selected Markdown storage and optional viewer mode.
Never inspect or import existing session files unless user selected exact paths,
scope, and confirmation.
