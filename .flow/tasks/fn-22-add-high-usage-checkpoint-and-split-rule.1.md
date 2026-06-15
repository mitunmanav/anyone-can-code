# fn-22-add-high-usage-checkpoint-and-split-rule.1 Implement high usage checkpoint and split rule

## Description
TBD

## Acceptance
- Unit tests prove continue/checkpoint/split/stop thresholds at 84/85/90/94.
- Front-door metadata exposes the usage checkpoint contract.
- Orchestrator/status/resume/verify docs require checkpoint or split before high usage burns the chat.
- Doctor reports the rule as available.
- Existing usage-budget estimates and receipts still pass.
- Flow validate, Doctor, compile, and relevant tests pass.


## Done summary
High-usage checkpoint and split rule implemented. ACC now checkpoints at 85%, splits at 90%, and stops at 94% unless user explicitly chooses otherwise.
## Evidence
- Commits:
- Tests: 144 unittest tests OK
- PRs: