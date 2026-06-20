# Add compaction and abort re-anchor recovery

## Description
Fix the Zenfit compaction/abort gap. After compaction, failed patch, abort, or rollback, ACC must visibly re-anchor from project files before continuing, so it does not proceed from stale chat memory.

## Acceptance
- Runtime instructions require re-reading project state after compaction, abort, failed patch, or rollback.
- Assistant-visible response must say what was re-read and what changed before continuing.
- Tests or QA simulate interrupted context and prove re-anchor happens before next write.
- Installed-runtime QA includes this recovery behavior.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
