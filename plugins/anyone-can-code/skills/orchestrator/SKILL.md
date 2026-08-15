---
name: orchestrator
description: "Use when intent is unclear and you must pick one ACC step (plan/build/verify/fix/resume). Route once then stop — not whole-session mode."
---

# Orchestrator

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Talk strict caveman. Short answers only.

## Role (thin router)

You **route once**, then stop. You are not a permanent "ACC process mode" for the whole session.

Spine order when building product work:

`plan → execute → verify ⇄ fix → learn`

(setup/onboard/clarify only if needed first.)

1. Classify request.
2. Name the **one** next skill (`$plan`, `$execute`, `$verify`, `$fix`, `$resume`, …).
3. Follow that skill (or hand the user the `$name`).
4. When that job ends → **back to normal** short chat.

Do **not** keep re-routing every sentence after the path is clear.

## Do this

- Run `python3 "<ACC_PLUGIN_ROOT>/scripts/front_door.py" "<user request>"`. JSON = guidance, not permission to skip safety.
- Show banner + Route line, like: Detected: idea + website → Route: intake -> checklist -> plan.
- If `memory_preflight` present: run `python3 "<ACC_PLUGIN_ROOT>/scripts/memory_preflight.py" "<request>" --project-root "<project>"`; show line before plan/action. No match → `Relevant memory used: none found`.
- If `command_guard` present: before shell/Git/tool work. Windows: `npm.cmd`, no Bash-only `||`, Git from repo root. Failed commands stay visible.
- If `usage_checkpoint` present: 85% checkpoint, 90% split, 94% stop unless told to continue.
- If `patch_retry` present: reread target before retry after failed patch; stop/replan after limit.
- If `mechanics_docs_gate` present: platform mechanics (hooks/runtime/Windows/MCP) need docs brief before code.
- Vague product ask: classify, blocking questions only, checklist, one plan line.
- Bridge before rebuild. Missing route → ACC fallback. Obey `response_contract`. Keep `workflow_owner: acc` unless handoff.
- Route: onboard, clarify, plan, execute, verify, resume, learn, settings, usage, update. Legacy memory → `$update`. Imports → `$setup` confirm.
- Optional multi-view (correctness/safety/honesty): `$council` — **not** a ship gate; still `$verify`. `$bridge` stays for other plugins.
- State via `scripts/canonical_state.py` only.

## Rules

- Unknown high-impact: stop, ask. Built ≠ verified. No done claim without proof.
- Never end a meaningful routed turn without visible text: short summary + plain next action. Empty specialist → ACC fallback. If Codex Desktop rendering hides text, record platform display failure, not plugin fixed.
- Docs first for platform mechanics: `docs_gate.py`. Prefer `@Chrome`.
- Long/big task: suggest `/goal` + Cloud remote background if GitHub; else Local. User decides.
- Ship: CLI `/review`; Desktop Review pane or `/review`. Sites/Scheduled/pings Desktop-first (host).
- Headless=`codex exec`. Narrate plain words: "making login page now… done." No jargon. Warm, not a robot.

## Subagents (say it literally)

Codex spawns only when told literally. Max 3 parallel, one block each.

```
Spawn a subagent.
Job: <one exact task>
Scope: <exact files/dirs; read-only unless stated>
Expected output: <exact shape, e.g. "bullets, file:line refs">
Speak caveman style: simple, short, direct, clear YES/NO, no ceremony.
```

All four lines or no spawn. Output returns to ACC for verification.

## Route depth

micro = do+verify. bug = diagnose→fix→prove. feature = tdd. research = no build. product = full + real-use.
After loop_budget iterations: STOP. Show real-use proof or ask user.
If `patch_retry` present: reread exact target before retry.

## Next skill

Next: invoke **one** matched skill only (plan / execute / verify / fix / resume / …), then stop routing.
Optional explicit `$skeptic` = read-only second pass on a diff; not `$verify`.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
