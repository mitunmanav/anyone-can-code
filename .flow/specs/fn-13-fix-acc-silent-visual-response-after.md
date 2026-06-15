# Fix ACC silent visual response after routed request

## Problem

On 2026-06-14 in the separate `website portfolios` project, user invoked ACC after update. ACC showed progress and selected `anyone-can-code:help`, but after the user asked to improve the existing website into a polished demo site, the visible assistant answer area stayed empty/silent for about 1 minute. The progress panel moved, but the user did not receive a clear next response.

## User-visible failure

- User sees ACC "worked" but no useful visible reply.
- User cannot tell whether ACC is thinking, stuck, waiting, or done.
- This damages trust even if background state changed correctly.

## Requirements

- R1: ACC must always produce a visible user-facing response after a routed user request, even when it needs clarification or hands off to another skill.
- R2: If ACC routes to help/status/brainstorming/design flow, the user must see a clear next action, not just progress UI.
- R3: Silent completion after meaningful user input must be treated as a bug and covered by regression proof.
- R4: Verification should reproduce or simulate the no-visible-response path from a normal project outside Plugin development.
- R5: Plugin development project must keep ACC disabled as helper while this is investigated.

## Evidence

- Screenshot provided by user: `codex-clipboard-fb75d75f-4567-4fac-961a-57d088b4f9a1.png`.
- Context: `website portfolios` project, after ACC update and Codex restart.
- Observed text before the silent turn: ACC help said state idle, no goal/task/plan, next best move is to tell build outcome in one sentence.
- User then requested: improve the existing website until it is a perfect demo site, using ACC, brainstorming, product design, and UI skills.

## Status

Captured only. No fix attempted yet.
