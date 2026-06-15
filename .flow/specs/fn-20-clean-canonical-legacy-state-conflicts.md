# fn-20-clean-canonical-legacy-state-conflicts Clean canonical legacy state conflicts

## Overview
Old session-shaped workflow files can contain legacy truth fields that disagree
with canonical verification. ACC must not let `status_line`, `work_state`,
`verification_state`, `states`, top-level `evidence`, or top-level `unverified`
override canonical truth.

## Scope
- Strip legacy truth fields on canonical state read/write.
- Preserve compatibility fields that are still settings/readiness metadata.
- Make Doctor report remaining raw legacy truth fields.
- Update status/resume/orchestrator docs to trust canonical verification only.
- Add regressions based on old session conflict shape.

## Approach
- Add a central legacy-field list in `scripts/canonical_state.py`.
- Sanitize existing workflow JSON before merging with canonical defaults.
- Sanitize updates before writing canonical workflow JSON.
- Change Doctor observability check from legacy `states/status_line` to
  canonical verification shape.

## Quick commands
<!-- Required: at least one smoke command for the repo -->
- `python -m unittest plugins.anyone-can-code.tests.test_project_state`
- `python plugins/anyone-can-code/scripts/doctor.py --json`

## Acceptance
- [ ] Old raw workflow with verified legacy fields and unverified canonical
  verification reads/writes as canonical unverified.
- [ ] Setup rewrites current project state without legacy truth fields.
- [ ] Doctor reports `legacy_state_fields`.
- [ ] Status/resume/orchestrator docs tell ACC not to trust legacy truth.
- [ ] Full tests, compile, Doctor, and Flow validation pass.

## References
- [[36 Manual Usage Session Audit 2026-06-14]]
