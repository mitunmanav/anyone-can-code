# fn-11-build-acc-codex-desktop-reliability-and.9 Build Doctor recovery and conflict control

## Description
TBD

## Acceptance
- [x] Doctor checks installed source, state agreement, hooks, memory, and recovery.
- [x] Plugin conflicts have explicit ownership and fallback.
- [x] Another plugin is never edited silently to repair ACC.
- [x] Recovery explains failure and safe next action in plain language.


## Done summary
Implemented Doctor recovery and conflict control. Doctor now checks installed ACC source, state agreement, hook health, memory, runtime agreement, and plugin conflict ownership. Recovery output gives plain next action. ACC never silently edits another plugin to repair ACC.
## Evidence
- Commits:
- Tests: python -m unittest discover plugins/anyone-can-code/tests (84 OK), python -m compileall plugins/anyone-can-code/scripts plugins/anyone-can-code/hooks/scripts plugins/anyone-can-code/mcp, python plugins/anyone-can-code/scripts/doctor.py --json (31 PASS, 0 WARN, 0 FAIL), python .flow/bin/flowctl.py validate --spec fn-11-build-acc-codex-desktop-reliability-and --json, git diff --check
- PRs:
