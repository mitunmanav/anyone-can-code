# fn-17-prove-requested-specialist-use-or.1 Account for requested specialist use and fallback

## Description
TBD

## Acceptance
﻿- Account for every explicitly requested specialist/capability in the front-door route result.
- Prove matched requested specialists from installed metadata/health, not weak token overlap alone.
- Report ACC fallback for missing/unhealthy requested specialists.
- Preserve ACC workflow ownership and fn-16 containment.
- Update bridge/orchestrator docs and verification evidence.


## Done summary
Implemented requested-specialist accounting in ACC front door and bridge docs.

Changes:
- Added explicit specialist intent detection for requested brainstorming, Product Design, Build Web Apps, UI skills, and browser specialists.
- Added requested_specialists route output that marks each requested specialist as matched from installed metadata/health or falling back to ACC with reason.
- Preserved ACC workflow ownership and existing single best plugin route behavior.
- Extended Doctor/front-door smoke to prove requested specialist accounting.
- Updated bridge/orchestrator/README/validation docs and Obsidian notes.

Verification:
- Focused front-door tests: 24 passed.
- Full plugin tests: 110 passed.
- Python compile passed.
- Doctor: 34 PASS / 0 WARN / 0 FAIL.
- Flow validation: 17 specs, 57 tasks, valid.

Limits:
- Installed Codex Desktop QA remains useful before release.
- No ACC runtime/hooks, Session Analyzer, commit, push, PR, tag, release, or publish action occurred.
## Evidence
- Commits:
- Tests:
- PRs: