---
satisfies: [R5, R6, R7, R9, R11, R12, R17]
---

## Description
Build full action timeline: pair tool calls/results, classify actions, measure outputs and retries, deduplicate compaction, and derive evidence-backed behavior and verification proxies.

**Size:** M
**Files:** `../session-analyzer/session_behavior.py`, `../session-analyzer/tests/test_session_behavior.py`, `../session-analyzer/docs/behavior-rules.md`

## Approach
- Pair built-in, custom, MCP, patch, browser, search, and deferred tool records by call ID and event semantics.
- Classify read/write/network/planning/verification actions through deterministic rules.
- Deduplicate one logical compaction from `compacted`, embedded `compaction`, and `context_compacted` records.
- Detect corrections, reversals, repeated failures, premature claims, aborts, rollbacks, and verification evidence as heuristics with confidence labels.

## Investigation targets
**Required:**
- `../session-analyzer/docs/event-schema.md` - call and compaction rules.
- `Projects/Anyone Can Code/24 Complete Session Timeline.md` - known action sequence.
- `Projects/Anyone Can Code/25 Learning and Memory Compliance.md` - correction chains.
- `Projects/Anyone Can Code/26 Session Findings and Roadmap.md` - behavior findings.
- `offical-codex-docs/core/prompting.md` - agent loop and compaction.

**Optional:**
- `offical-codex-docs/core/subagents.md` - parallel-work cost signals.
- `offical-codex-docs/core/hooks.md` - tool and lifecycle event names.

## Acceptance
- [ ] Insight candidates receive deterministic confidence, impact, recurrence, and verification-strength fields.
- [ ] Ranking rules favor supported operational evidence and demote weak or low-sample correlations.
- [ ] All current tool types are counted and paired where evidence permits; orphaned records are explicit.
- [ ] Tool metadata includes sanitized inputs, output sizes, success/failure, duration, repeats, and sequence.
- [ ] Current thread-2 evidence reports one logical compaction and links its related records.
- [ ] Turn timeline includes completion, first-token latency, duration, abort, rollback, correction, claim, and verification signals.
- [ ] Behavior outputs distinguish exact facts from heuristic flags and never claim hidden intent.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
