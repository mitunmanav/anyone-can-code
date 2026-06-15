# fn-23-require-reread-after-failed-patch.1 Implement patch retry reread discipline

## Description
TBD

## Acceptance
- Unit tests prove patch retry is blocked after failure until exact target reread.
- Unit tests prove reread allows retry and max retry exhaustion blocks.
- Front-door metadata exposes the patch retry policy.
- Orchestrator/execute/status/verify docs require reread-before-retry.
- Doctor reports the policy as available.
- Flow validate, Doctor, compile, and relevant tests pass.


## Done summary
Patch retry discipline implemented. After a failed patch, ACC must reread the exact target before retry and stop/replan after the bounded retry limit.
## Evidence
- Commits:
- Tests: 144 unittest tests OK
- PRs: