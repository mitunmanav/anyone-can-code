# Implement ACC core safe git workflow

## Description
Build the first ACC-owned safe git workflow path from the contract. The goal is not a broad VCS product. The goal is a reliable built-in path for common local checkpoint and commit operations that ACC can use without creating a project-specific replacement script.

## Acceptance
- ACC source contains a core safe git workflow module or script, not a Zenfit-only copy.
- It can inspect status, produce a plan, stage safe files, run configured verification, commit locally, and write receipts.
- It blocks risky files by default and explains why.
- It never pushes, opens PRs, tags, releases, merges, or touches remotes.
- Unit tests cover safe path, risky blocked path, unrelated dirty work preservation, verification failure, and receipt creation.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
