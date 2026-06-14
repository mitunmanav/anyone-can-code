# fn-11-build-acc-codex-desktop-reliability-and.2 Enforce workflow ownership and specialist boundaries

## Description
Enforce ACC as default workflow owner while still using installed plugins for
bounded specialist capability. Routing must keep ACC plan/state/user
communication, define specialist inputs/outputs/permissions/return path, block
foreign workflow controls, preserve usable technical output, and allow only
explicit user-approved ownership handoff.
## Acceptance
- [ ] ACC remains default workflow owner.
- [ ] Specialist work has bounded inputs, outputs, permissions, and return path.
- [ ] Foreign plans, trackers, commits, gates, and style takeovers are detected and blocked.
- [ ] Usable technical output survives takeover filtering and returns to ACC.
- [ ] Explicit user-approved handoff remains possible.
- [ ] Shipped bridge and orchestrator instructions match implemented behavior.
- [ ] Focused and full automated tests pass.
## Done summary
Implemented ACC workflow ownership and bounded specialist routing.

- ACC remains route and workflow owner by default.
- Specialist assignments define request, allowed output, permissions,
  forbidden workflow controls, return path, and explicit-handoff status.
- Foreign owner, plan, tracker, commit, approval-gate, and response-style
  controls are blocked while usable technical output is preserved.
- Explicit user-approved workflow handoff remains supported.
- Bridge, orchestrator, and README instructions match behavior.
- TDD tests proved missing behavior first, then passed.
## Evidence
- Commits:
- Tests: python -m unittest plugins.anyone-can-code.tests.test_front_door: 13 passed, python -m unittest discover -s plugins/anyone-can-code/tests -p test_*.py: 67 passed, python -m py_compile: passed, Doctor: 26 PASS, 0 WARN, 0 FAIL, Flow validation: 0 errors, 0 warnings
- PRs: