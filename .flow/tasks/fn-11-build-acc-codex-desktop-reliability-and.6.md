# fn-11-build-acc-codex-desktop-reliability-and.6 Build bounded task and subagent coordination

## Description
TBD

## Acceptance
- [x] Tasks have names, dependencies, ownership, status, and evidence.
- [x] Duplicate work is prevented through claims.
- [x] Subagents are used only with explicit user request where Codex requires it.
- [x] Parallel work stays bounded and returns concise evidence.


## Done summary
Added bounded task coordination with normalized task records, dependency checks, active claim locks, evidence-backed completion, and subagent assignment rules requiring explicit user request plus Codex need. Verified by 74 unit tests, Python compile, Doctor 26/0/0, Flow validate 0/0, and git diff --check.
## Evidence
- Commits:
- Tests:
- PRs: