# Enforce docs-first mechanics gate

## Problem

The docs-first mechanics gate exists only as a future note. ACC can still change hook, runtime, cache, UI lifecycle, telemetry, or Windows-specific platform behavior from session traces alone.

## Requirements

- Add a deterministic gate in product code for platform-mechanics changes.
- The gate must require a docs/source brief before implementation when work touches Codex Desktop mechanics, hooks, plugin runtime/cache, Windows launch behavior, UI lifecycle, telemetry/logs, or MCP/tool plumbing.
- Session traces may count as failure evidence, not as platform mechanics authority.
- If official docs/source are missing, require controlled proof and recorded uncertainty before code changes.
- Surface the gate through front-door route metadata, Doctor, repo docs, and relevant skills.

## Acceptance

- Unit tests prove normal product work can proceed, platform-mechanics work blocks without a docs brief, docs brief allows work, and controlled proof can allow work only with uncertainty recorded.
- Front-door route metadata exposes the mechanics docs gate.
- Orchestrator/plan/execute/verify/status docs require the gate.
- README/VALIDATION mention the hard product gate.
- Doctor reports the gate as available.
- Flow validate, Doctor, compile, and relevant tests pass.
