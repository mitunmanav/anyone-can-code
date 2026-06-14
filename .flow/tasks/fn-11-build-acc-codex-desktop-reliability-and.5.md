# fn-11-build-acc-codex-desktop-reliability-and.5 Build capability registry health and fallbacks

## Description
TBD

## Acceptance
- [x] Registry knows available capabilities, source, health, and fallback.
- [x] Capability is probed before important use.
- [x] Missing or unhealthy capability degrades cleanly.
- [x] Another plugin never becomes durable truth.


## Done summary
Added derived capability registry with provider/source/health/fallback records, pre-use probes, clean ACC degradation for unhealthy or failed capabilities, and explicit non-authoritative specialist state. Evidence: 72 unit tests passed; Python compile passed; Doctor 26 PASS, 0 WARN, 0 FAIL; Flow validation 0 errors, 0 warnings.
## Evidence
- Commits:
- Tests: 72 unit tests passed; Python compile passed; Doctor 26/0/0; Flow 0/0.
- PRs:
