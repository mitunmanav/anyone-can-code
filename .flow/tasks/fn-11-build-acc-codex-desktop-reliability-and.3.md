# fn-11-build-acc-codex-desktop-reliability-and.3 Build transactional canonical state

## Description
Create one transactional canonical workflow state for ACC. Goal, active task,
decisions, boundaries, progress, verification, failures, warnings, plan, tasks,
and next action live in one JSON truth. Status, queue, resume, active guidance,
and session snapshot are derived in the same transaction. Failed writes roll
back. Scope changes preserve old history and invalidate affected verification.
## Acceptance
- [ ] One canonical state is durable truth.
- [ ] Updates are transactional or roll back.
- [ ] Status, plan guidance, queue, resume, and snapshot derive from canonical state and share one transaction ID.
- [ ] Scope change preserves superseded history and invalidates stale verification.
- [ ] Setup and hook state writes use canonical transaction engine.
- [ ] Shipped plan, execute, resume, and status instructions match implemented behavior.
- [ ] Focused and full automated tests pass.
## Done summary
Implemented transactional canonical ACC state.

- `workflow.json` is one durable active truth.
- Status, task queue, resume note, active guidance, and session snapshot derive
  together and share one transaction ID.
- Failed writes roll back the whole transaction.
- Scope change preserves superseded goal/task history and invalidates affected
  verification.
- Setup and hook writes use canonical engine.
- Plan, execute, resume, and status instructions match behavior.
- TDD tests proved missing and rollback behavior first, then passed.
## Evidence
- Commits:
- Tests: python -m unittest plugins.anyone-can-code.tests.test_project_state: 29 passed, python -m unittest discover -s plugins/anyone-can-code/tests -p test_*.py: 67 passed, python -m py_compile: passed, Doctor: 26 PASS, 0 WARN, 0 FAIL, Flow validation: 0 errors, 0 warnings, git diff --check: passed
- PRs: