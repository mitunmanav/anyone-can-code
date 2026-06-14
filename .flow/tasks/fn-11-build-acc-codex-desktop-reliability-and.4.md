# fn-11-build-acc-codex-desktop-reliability-and.4 Build restart and compaction recovery

## Description
TBD

## Acceptance
- [x] Active-task capsule records goal, decisions, boundaries, evidence, and next action.
- [x] Capsule is saved before risky context transitions when possible.
- [x] Restart and compaction recovery re-anchor from canonical state.
- [x] Missing or uncertain context is reported.


## Done summary
Added canonical active-task capsules, pre-transition saves, restart/compaction re-anchoring, derived-view repair, explicit uncertainty reporting. Evidence: 70 unit tests passed; Python compile passed.
## Evidence
- Commits:
- Tests: 70 unit tests passed; Python compile passed.
- PRs:
