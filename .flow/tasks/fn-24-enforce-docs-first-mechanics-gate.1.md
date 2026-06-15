# fn-24-enforce-docs-first-mechanics-gate.1 Implement docs-first mechanics gate

## Description
TBD

## Acceptance
- Unit tests prove mechanics work blocks without docs/source brief.
- Unit tests prove docs brief allows work, and controlled proof allows only with uncertainty recorded.
- Front-door route metadata exposes mechanics docs gate.
- Orchestrator/plan/execute/verify/status docs require the gate.
- README/VALIDATION mention the hard gate.
- Doctor reports the gate as available.
- Flow validate, Doctor, compile, and relevant tests pass.


## Done summary
Docs-first mechanics gate implemented. Platform-mechanics work now requires a docs/source brief or controlled proof with uncertainty recorded before code changes.
## Evidence
- Commits:
- Tests: 144 unittest tests OK
- PRs: