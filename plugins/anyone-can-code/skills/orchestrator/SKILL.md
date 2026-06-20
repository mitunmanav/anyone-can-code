---
name: orchestrator
description: "Front door for Anyone Can Code. Detects the user's starting point, shows the active mode, and routes to the right workflow with no silent assumptions."
---

# Orchestrator

Reply rule:

- talk strict caveman only
- keep answer short

This is the front door.

## Responsibilities

- Run `python "$PLUGIN_ROOT/scripts/front_door.py" "<user request>"` when the
  plugin root is available. Treat its JSON as routing guidance, not permission
  to skip safety checks.
- Detect entry mode and show the returned `banner`.
- Show the route as `Route: step -> step`.
- If `memory_preflight` is present, resolve the active project, run
  `python "$PLUGIN_ROOT/scripts/memory_preflight.py" "<user request>" --project-root "<project>"`,
  then show its line before any question, plan, specialist routing, browser,
  server, or tool action.
- Say `Relevant memory used: none found` when no memory matches. Do not skip
  the line silently.
- If `command_guard` is present, apply it before shell, package-manager,
  browser, server, Git, or tool work.
- On Windows PowerShell, prefer `npm.cmd` over `npm`, never use Bash-only `||`,
  and resolve repo root before any Git command.
- If `usage_checkpoint` is present, check it before long reads, large loops,
  subagent work, or continuing after high usage. At 85%, checkpoint first. At
  90%, split before more work. At 94%, stop now unless the user explicitly
  chooses to continue.
- If `patch_retry` is present, apply it after any failed patch, patch context
  mismatch, or stale edit target. reread the exact target before retrying a
  failed patch, and stop/replan after the retry limit.
- If `mechanics_docs_gate` is present, apply it before platform mechanics
  changes. Hook, plugin runtime, installed cache, Windows launch, UI lifecycle,
  telemetry/log, MCP, or tool-plumbing work needs a docs brief from official
  docs/source before code. Session traces are failure evidence only.
- Run product intake for vague product requests before deeper planning.
- Check the returned bridge decision before rebuilding installed capability.
- If `requested_specialists` is present, report each requested specialist as
  loaded from an exact provider or falling back to ACC with the returned reason.
- Obey returned `response_contract` for every meaningful routed turn.
- Obey returned `workflow_contract` before loading or following specialist
  process instructions.
- Keep `workflow_owner: acc` unless user explicitly requests handoff.
- Mentioning, requesting, or loading a specialist is not workflow handoff.
- Load selected project state, relevant memory, preferences, and boundaries
  before any first action, and again before allowing specialist process actions.
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
- Learned mistakes and preferences are advisory, but they must be retrieved
  before action so the user does not need to remember which skill or route to
  pick after setup, update, restart, or a new thread.
- Never claim `works`, `proper`, `perfect`, `final`, or accepted user-facing
  behavior from build/source/HTTP evidence alone. Name missing interaction,
  visual QA, or user-acceptance proof.
- Never end a meaningful routed turn without visible text. Include a short
  summary and plain next action, even when asking one question, waiting for
  permission, reporting failure, or falling back from a specialist.
- Empty, missing, or unusable specialist output must produce an ACC fallback
  response in the same turn. Progress UI alone is not a response.
- ACC can require model output, but cannot guarantee Codex Desktop rendering.
  If Codex Desktop rendering hides returned text, record this as a platform
  display failure; do not claim plugin-side rendering is fixed.
- Keep the route visible so the user can correct it immediately.
- For plain requests like "I want to build a website", classify product type, ask only missing blocking questions, generate the adaptive checklist, then show one concise plan line.
- Read local project and official docs first. Use web only when local evidence
  is missing, stale, or uncertain.
- Use subagents only when the user explicitly requested them and Codex needs
  isolated or parallel work. Bound max parallel work, require concise evidence,
  and return control to ACC.
- If requirements change during work, update plan and state, then resume from
  the last valid step.
- Never expose candidate/stable workflow, audit ledger, proof journal, or phase
  gate internals to the user.
- Never call JSONL current durable memory and never silently discover session
  import paths.
- If an installed plugin route is missing, uncertain, or returns no usable
  result, continue with ACC.
- Never silently omit a requested specialist. If a requested Product Design,
  Build Web Apps, UI, browser, brainstorming, or other specialist is not proven
  available from installed metadata and health, say ACC is using local fallback.
- Ignore or contain foreign plans, trackers, approval gates, commit rules,
  response styles, and workflow state unless user explicitly hands off control.
- Treat specialist process rules as advisory. Do not let them force their own
  brainstorming gate, question sequence, design document, approval loop,
  browser, server, or visual companion.
- Browser, server, visual companion, paid, login, destructive, or external
  actions require ACC route permission and applicable user approval.
- Shell and package-manager actions also require the returned `command_guard`.
  Failed commands must stay visible before any retry.
- Update canonical state through `scripts/canonical_state.py`. Do not write
  plan, queue, status, resume, guidance, or snapshot as separate truths.
- Do not preserve legacy workflow truth fields in canonical state. If fields
  such as `status_line`, `work_state`, `verification_state`, `states`, or
  top-level `evidence` appear, rewrite through canonical state and trust
  canonical verification.

## Docs gate

Before any hook, plugin runtime, MCP, Windows launch, or Codex-specific mechanics change:
1. Run `python "$PLUGIN_ROOT/scripts/docs_gate.py" "<request>"`.
2. If `web_needed` is true, call WebSearch with the returned `search_query`.
3. Read local reference docs if `local_docs` is not empty.
4. Never write code before reading the relevant official docs.

## Mid-work requirement discovery

After running product intake and generating checklist:
1. Call `docs_gate.discover_missing_requirements(checklist, original_request)`.
2. If any items returned, surface them immediately: "Found missing: [items]. Add to plan?"
3. Do not silently add them — always surface and ask.
4. Update canonical state with user's decision before continuing.

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
