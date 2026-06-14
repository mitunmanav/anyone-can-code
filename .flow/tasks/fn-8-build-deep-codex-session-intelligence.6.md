---
satisfies: [R1, R3, R5, R6, R10, R12, R13, R14, R15, R16, R17]
---

## Description
Run full safety, correctness, determinism, scale, and privacy verification against real golden evidence and adversarial synthetic fixtures; record complete evidence in Flow and Obsidian.

**Size:** M
**Files:** `../session-analyzer/tests/`, `../session-analyzer/README.md`, `Projects/Anyone Can Code/27 Session Analyzer Architecture.md`, `Projects/Anyone Can Code/28 Session Analyzer Deep Upgrade Request.md`, `Projects/ACC Session Analyzer Dump/`

## Approach
- Re-run all legacy safety tests plus new golden/adversarial suites.
- Verify input hashes before and after real run.
- Compare exact metrics with approved corrected audit facts.
- Measure runtime, output sizes, deterministic-file hashes, and bounded-memory behavior.
- Record warnings and unresolved schema gaps; do not call partial evidence complete.

## Investigation targets
**Required:**
- `../session-analyzer/tests/test_session_analyzer.py` - legacy safety suite.
- All task .1-.5 test modules and metric contracts.
- `Projects/Anyone Can Code/23 Session Audit Master.md` - golden results.
- `Projects/Anyone Can Code/27 Session Analyzer Architecture.md` - isolation contract.
- `Projects/Anyone Can Code/28 Session Analyzer Deep Upgrade Request.md` - user intent and knowledge limits.

**Optional:**
- `offical-codex-docs/core/pricing.md`
- `offical-codex-docs/core/hooks.md`

## Acceptance
- [ ] Instrumented verification proves one source parse pass produces both output layers.
- [ ] Every compact ranked finding resolves to existing forensic evidence IDs and metric formulas.
- [ ] All legacy and new tests pass with exact command evidence.
- [ ] Real-source hashes remain unchanged and runtime reads only fixed inbox files.
- [ ] Golden facts match R12, including corrected token totals and one logical compaction.
- [ ] Adversarial tests cover malformed, unknown, duplicate, missing, out-of-order, truncated, huge, reset-counter, and privacy cases.
- [ ] Deterministic analytical files hash-match across repeated controlled runs except documented run metadata.
- [ ] Obsidian and Flow evidence state what passed, warnings, unknowns, and that no GitHub or ACC runtime action occurred.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
