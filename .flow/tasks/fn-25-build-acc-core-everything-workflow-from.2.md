# Design built-in safe git workflow contract

## Description
Turn the Zenfit git-manager prototype into an ACC core contract. ACC should not need each project to invent a separate local manager for common safe git work. Define what ACC itself owns, what remains user-confirmed, and what stays blocked.

## Acceptance
- Contract defines status, plan, manage, verify, commit, and receipt behavior.
- Contract classifies changes as safe, risky, or blocked.
- Contract protects .codex runtime files, env/secrets, unrelated user work, generated dumps, analyzer artifacts, and remote actions.
- Push, PR, tag, release, merge, and remote branch mutation remain explicit-command only.
- Contract records checkpoint, rollback path, verification command result, staged files, commit id, and skipped files.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
