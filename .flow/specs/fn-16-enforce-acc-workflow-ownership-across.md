# Enforce ACC workflow ownership across specialist skills

## Problem

During June 14 real use, Superpowers brainstorming rules shaped the workflow before ACC loaded project memory and preferences. It created an external five-step process and offered visual companion/browser behavior despite saved ACC ownership and no-browser rules. Existing takeover protection only inspects some top-level plugin result fields after specialist execution.

## Requirements

- R1: Every routed request carries an explicit ACC workflow contract unless user explicitly hands off ownership.
- R2: Mentioning or requesting a specialist skill is not workflow handoff.
- R3: Specialist process instructions are advisory and cannot replace ACC plan, tracker, approvals, commits, response style, state, or route.
- R4: Project memory, preferences, boundaries, and current state are loaded before specialist process actions.
- R5: Browser, server, visual companion, paid, login, destructive, and external actions require ACC route permission and applicable user approval.
- R6: Specialist assignments contain allowed output, allowed actions, forbidden controls, return path, and project constraints.
- R7: Returned specialist results are scanned recursively for takeover controls. Preserve bounded technical output; strip/ignore foreign controls and report exact blocked paths.
- R8: Explicit user handoff remains supported and must be exact, not inferred from a plugin mention.
- R9: ACC canonical workflow owner stays `acc` after contained specialist use.

## Scope

Strengthen front-door workflow contract, bounded assignments, recursive result containment, orchestrator/bridge guidance, tests, Doctor smoke, repo docs, Flow, and Obsidian.

## Out of Scope

Whether requested specialists were actually found/used is next ordered issue. Do not change Session Analyzer, hooks, installed runtime, or remote state.

## Verification

Test exact June request, mention-versus-handoff, nested takeover fields, visual companion/browser process attempts, technical output preservation, explicit handoff, full tests, compile, Doctor, Flow, and diff integrity.

## Decision Context

Selected deterministic pre-work contract plus recursive post-result containment. Existing top-level-only filtering is insufficient. Reject blanket specialist ban because bounded technical help remains useful.
