---
satisfies: [R3, R8, R9, R11, R12]
---

## Description
Build exact token, context-window, rate-limit, model, reasoning-effort, and timing metrics from normalized records, with explicit formulas and consistency checks.

**Size:** M
**Files:** `../session-analyzer/session_metrics.py`, `../session-analyzer/tests/test_session_metrics.py`, `../session-analyzer/docs/metric-formulas.md`

## Approach
- Use final cumulative token snapshot per session for session totals.
- Use `last_token_usage` and adjacent cumulative snapshots for turn/delta validation.
- Calculate cached and uncached input, context utilization, rate-limit trajectories, reset times, duration, and first-token latency.
- Correlate model and effort only with observable outcomes and include sample-size/causation warnings.

## Investigation targets
**Required:**
- `../session-analyzer/docs/event-schema.md` - token snapshot semantics.
- `Projects/Anyone Can Code/23 Session Audit Master.md` - corrected token/effort evidence.
- `offical-codex-docs/core/models.md` - model choices.
- `offical-codex-docs/core/pricing.md` - tokens, limits, and efficiency guidance.
- `offical-codex-docs/learn/best-practices.md` - task-aware effort guidance.

**Optional:**
- `offical-codex-docs/core/speed.md` - speed/credit distinction.

## Acceptance
- [ ] Current corpus produces exact corrected per-session and combined final counters.
- [ ] Repeated cumulative snapshots are never added together.
- [ ] Resets, missing snapshots, inconsistent deltas, and absent rate-limit fields produce warnings, not invented values.
- [ ] Metrics expose formulas, source references, validation state, and schema version.
- [ ] Reasoning records report effort, token counts, encrypted-size metadata, and limitations without exposing hidden reasoning.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
