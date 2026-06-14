---
satisfies: [R1, R2, R3, R6, R12, R13, R14, R15]
---

## Description
Define exact observable-data contract before parser changes. Inventory current two exports, classify logical events, write formula rules, and lock private golden expectations for corrected counts.

**Size:** M
**Files:** `../session-analyzer/docs/event-schema.md`, `../session-analyzer/tests/fixtures/`, `../session-analyzer/tests/test_golden_contract.py`, `Projects/Anyone Can Code/28 Session Analyzer Deep Upgrade Request.md`

## Approach
- Reuse source-hash and read-only boundary behavior from `../session-analyzer/session_analyzer.py:79-147`.
- Derive event semantics from current exports and local official Codex docs.
- Separate stable documented concepts from version-specific observed transcript fields.
- Define cumulative-versus-delta token formulas and logical-event deduplication before implementation.

## Investigation targets
**Required:**
- `../session-analyzer/session_analyzer.py:180-281` - current incorrect recursive semantic counting.
- `../session-analyzer/tests/test_session_analyzer.py` - existing safety baseline.
- `Projects/Anyone Can Code/23 Session Audit Master.md` - corrected golden facts.
- `offical-codex-docs/core/prompting.md` - loop, context, compaction.
- `offical-codex-docs/core/hooks.md` - transcript instability and event concepts.

**Optional:**
- `Projects/Anyone Can Code/24 Complete Session Timeline.md`
- `Projects/Anyone Can Code/26 Session Findings and Roadmap.md`

## Acceptance
- [ ] Schema contract lists record types, key fields, provenance, logical deduplication, unknown handling, and stability status.
- [ ] Golden expectations include source hashes, 1,789 records, zero parse failures, 53 turn contexts, corrected 17,942,734 combined tokens, full tool inventory, and one logical compaction.
- [ ] Reasoning and intelligence limits explicitly reject hidden-chain, weights, training-data, and causation claims.
- [ ] No implementation parser behavior changes in this task until contract evidence is reviewable.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
