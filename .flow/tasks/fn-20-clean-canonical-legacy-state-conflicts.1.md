# fn-20-clean-canonical-legacy-state-conflicts.1 Remove stale legacy workflow truth

## Description
Remove stale legacy workflow truth from canonical state so old generated fields
cannot claim verified when canonical verification says unverified/stale.

## Acceptance
- [x] Canonical reader/writer strips legacy truth fields.
- [x] Doctor warns if raw workflow still contains legacy truth.
- [x] Setup/update path can rewrite state cleanly.
- [x] Tests cover old-session conflict shape.
- [x] Docs and Obsidian are updated.

## Done summary
Canonical state strips stale legacy workflow truth fields. Doctor reports legacy_state_fields. Status/resume/orchestrator docs trust canonical verification. Verification: 122 tests, compile, Doctor 36/0/0, Flow valid.
## Evidence
- Commits:
- Tests:
- `python -m unittest discover -s plugins\anyone-can-code\tests` - 122 passed.
- `python -m compileall plugins\anyone-can-code` - passed.
- `python plugins\anyone-can-code\scripts\doctor.py --json` - 36 PASS / 0 WARN / 0 FAIL.
- `python .flow\bin\flowctl.py validate --all` - 20 specs / 60 tasks / valid.
- PRs:
