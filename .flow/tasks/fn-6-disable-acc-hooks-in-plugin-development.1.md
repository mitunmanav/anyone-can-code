# fn-6-disable-acc-hooks-in-plugin-development.1 Implement ACC-only tree hook disable

## Description
TBD

## Acceptance
ACC hooks alone are disabled below the Plugin development parent marker.
All five hook entry points return `{}` and do no writes.
Outside projects retain normal ACC hook behavior.
Remove broad hook feature disable settings, update docs, install refreshed runtime, and verify no GitHub action.


## Done summary
Disabled only ACC lifecycle hooks throughout the Plugin development directory tree.

- Added an ancestor marker contract checked by every ACC hook before side effects.
- Kept ACC skills, MCP, Flow-Next hooks, and other plugin hooks active.
- Removed broad hook-disable settings from live and reference project configs.
- Added Doctor reporting, regression tests, docs, and project-history records.
- Verified normal ACC hook behavior remains available outside the marked tree.
- No GitHub action was taken.
## Evidence
- Commits:
- Tests: python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py, python -m py_compile plugins\anyone-can-code\hooks\scripts\state.py plugins\anyone-can-code\hooks\scripts\guard.py plugins\anyone-can-code\hooks\scripts\audit.py plugins\anyone-can-code\hooks\scripts\load_session.py plugins\anyone-can-code\hooks\scripts\save_session.py plugins\anyone-can-code\scripts\doctor.py plugins\anyone-can-code\scripts\runtime_info.py, python plugins\anyone-can-code\scripts\doctor.py --json, python .flow\bin\flowctl.py validate --all
- PRs: