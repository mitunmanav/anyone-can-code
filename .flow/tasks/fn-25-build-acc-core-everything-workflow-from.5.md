# Make learning evidence provable

## Description
Fix the difference between explicit learning that wrote a durable note and auto-learning that had no proof. ACC must prove learning behavior: either it captured a durable note/receipt, or it clearly says no auto-learning happened.

## Acceptance
- Explicit learn writes durable memory and performs readback proof.
- Auto-learning has documented trigger rules and durable evidence when it runs.
- If auto-learning does not run, ACC reports no auto-learning evidence instead of implying it learned.
- Hook-managed learning is either implemented with logs/receipts or explicitly not claimed.
- Tests cover explicit learn readback and auto-learning evidence/no-evidence paths.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
