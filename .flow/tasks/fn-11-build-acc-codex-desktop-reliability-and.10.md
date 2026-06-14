# fn-11-build-acc-codex-desktop-reliability-and.10 Add usage budgets and visible background work

## Description
TBD

## Acceptance
- [x] Context cost is estimated before large reads or loops.
- [x] Tool evidence is compacted into receipts.
- [x] Usage warnings state uncertainty.
- [x] Background work is visible, stoppable, bounded, and receipt-producing.
- [x] Normal work uses cheap checks; deep checks are risk-based.


## Done summary
Implemented usage budgets and visible background work. Added approximate context estimates before large reads/loops, compact tool-evidence receipts, bounded/stoppable background-work receipts, and risk-based cheap/deep check selection. Doctor now verifies this support.
## Evidence
- Commits:
- Tests: python -m unittest plugins.anyone-can-code.tests.test_project_state (47 OK), python plugins/anyone-can-code/scripts/doctor.py --json (32 PASS, 0 WARN, 0 FAIL)
- PRs:
