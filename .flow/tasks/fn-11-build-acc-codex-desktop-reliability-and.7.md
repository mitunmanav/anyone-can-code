# fn-11-build-acc-codex-desktop-reliability-and.7 Redesign hooks as optional measured helpers

## Description
TBD

## Acceptance
- [x] Each hook has one measurable purpose.
- [x] Core operation works when hooks are absent or fail.
- [x] Repair retries are bounded.
- [x] Circuit breaker stops cross-layer repair loops.
- [x] Real restart proof is required before fixed claims.


## Done summary
Redesigned hooks as optional measured helpers with one declared purpose per hook, health ledger, bounded two-failure retry, circuit breaker, safe empty fallback on hook failure, and restart/new-thread proof requirement before fixed claims.
## Evidence
- Commits:
- Tests:
- PRs: