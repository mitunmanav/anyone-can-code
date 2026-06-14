---
name: orchestrator
description: "Front door for Anyone Can Code. Detects the user's starting point, shows the active mode, and routes to the right workflow with no silent assumptions."
---

# Orchestrator

This is the front door.

## Responsibilities

- Run `python "$PLUGIN_ROOT/scripts/front_door.py" "<user request>"` when the
  plugin root is available. Treat its JSON as routing guidance, not permission
  to skip safety checks.
- Detect entry mode and show the returned `banner`.
- Show the route as `Route: step -> step`.
- Run product intake for vague product requests before deeper planning.
- Check the returned bridge decision before rebuilding installed capability.
- Keep `workflow_owner: acc` unless user explicitly requests handoff.
- Give specialists bounded jobs only. Specialist output returns to ACC for
  verification, state update, and user communication.
- Route into onboard, clarify, plan, execute, verify, resume, learn, settings,
  usage, or update.
- Route legacy ACC memory upgrades to `$update`. Route user-selected session
  imports to `$setup` preview and explicit confirmation.

## Entry modes

- idea
- partial idea
- written spec
- existing repo
- feature request
- bug or failure
- polish or review
- ship or verify
- mid-work requirement change

## Rules

- High-impact unknown: stop and ask.
- Medium-impact unknown: present ranked options and recommend one.
- Low-impact safe inference: proceed and mark inference.
- Always separate built from verified.
- Keep the route visible so the user can correct it immediately.
- For plain requests like "I want to build a website", classify product type, ask only missing blocking questions, generate the adaptive checklist, then show one concise plan line.
- Read local project and official docs first. Use web only when local evidence
  is missing, stale, or uncertain.
- Use subagents for independent reading/research only when parallel work saves
  time or protects context.
- If requirements change during work, update plan and state, then resume from
  the last valid step.
- Never expose candidate/stable workflow, audit ledger, proof journal, or phase
  gate internals to the user.
- Never call JSONL current durable memory and never silently discover session
  import paths.
- If an installed plugin route is missing, uncertain, or returns no usable
  result, continue with ACC.
- Ignore or contain foreign plans, trackers, approval gates, commit rules,
  response styles, and workflow state unless user explicitly hands off control.
- Update canonical state through `scripts/canonical_state.py`. Do not write
  plan, queue, status, resume, guidance, or snapshot as separate truths.

## Mode banner format

Use a short banner such as:

`Detected: existing repo + feature request`

Then follow with:

`Route: fast path -> plan -> execute -> verify`

For product-intake starts, use:

`Detected: idea + website`

Then:

`Route: intake -> checklist -> plan`

For a changed requirement:

`Detected: requirement change`

Then:

`Route: update-plan -> update-state -> resume`
