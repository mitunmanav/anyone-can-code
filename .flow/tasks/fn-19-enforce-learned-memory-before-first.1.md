# fn-19-enforce-learned-memory-before-first.1 Make learned mistakes drive first action

## Description
Make learned mistakes drive ACC's first action after setup, update, restart, or
new thread. User should not need to know which skill/workflow to pick. ACC must
retrieve top relevant memory first and show the result line.

## Acceptance
- [x] Add memory preflight route contract.
- [x] Add executable memory preflight helper.
- [x] Add tests for route contract, configured memory path, post-rerun recall,
  and Doctor check.
- [x] Update installed skill docs and repo validation docs.
- [x] Update Obsidian project brain.

## Done summary
Memory preflight enforced before ACC first action. Added source helper, route contract, Doctor check, docs, tests, and Obsidian record. Verification: 120 tests, compile, Doctor 35/0/0, Flow valid.
## Evidence
- Commits:
- Tests:
- `python -m unittest discover -s plugins\anyone-can-code\tests` - 120 passed.
- `python -m compileall plugins\anyone-can-code` - passed.
- `python plugins\anyone-can-code\scripts\doctor.py --json` - 35 PASS / 0 WARN / 0 FAIL.
- `python .flow\bin\flowctl.py validate --all` - 19 specs / 59 tasks / valid.
- Installed runtime proof added 2026-06-15:
  `.codex\anyone-can-code\artifacts\installed-qa\installed-qa-20260615T064937Z-e8fb67b8.json`
  passed after local installed cache backup/refresh. `memory_write_through`
  proved store, setup, update, and new-thread recall before first action.
  Each recall returned `Relevant memory used: 1 item(s)`.
- PRs:
