## Description
Migrate legacy JSONL memory and user-selected existing local session files to Markdown. Update all affected prior ACC surfaces from completed tasks `.1` through `.4`: setup, update, Doctor, learn, status, help, onboard, orchestrator, README, validation, generated state, and source-of-truth docs.

## Acceptance
- [x] Legacy JSONL is backed up before migration.
- [x] Existing session files are backed up or snapshotted before import.
- [x] Migration is deduplicated, resumable, and idempotent.
- [x] Legacy data remains until Markdown verification passes.
- [x] Imported session lessons include provenance, scope, and source receipt.
- [x] Failure creates a rollback receipt and leaves source data intact.
- [x] All affected earlier task surfaces point to the new memory contract.
- [x] Installed-runtime upgrade path is documented.

## Done summary
Built safe JSONL/session-to-Markdown migration. Sources are backed up or snapshotted before writes, repeated imports skip stable hashes, written notes carry scope/provenance/source receipt, verification gates success, failures restore prior Markdown and write rollback receipts. Updated setup, update, Doctor, learn, status, help, onboard, orchestrator, docs, validation, generated project guidance, and upgrade flow.
## Evidence
- Commits: `4c9a731 Migrate legacy memory to Markdown safely`
- Tests: python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py: 49 passed, python -m py_compile required plugin scripts: passed, python plugins\anyone-can-code\scripts\setup.py .: setup smoke passed, python plugins\anyone-can-code\scripts\doctor.py --json: 26 PASS, 0 WARN, 0 FAIL, python .flow\bin\flowctl.py validate --all --json: 5 specs, 17 tasks, 0 errors, 0 warnings
- PRs:
