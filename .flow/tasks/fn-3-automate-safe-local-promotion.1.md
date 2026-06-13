# fn-3-automate-safe-local-promotion.1 Add scoped promotion guard

## Description
Build a tiny local scope guard for promotion into `main`.

The guard must be deterministic and cheap: use only PowerShell and Git. It must compare a base ref and candidate ref, apply a named policy, and fail if forbidden files appear. Update workflow docs and record evidence in Flow/Obsidian.
## Acceptance
- [ ] Tests prove reliability policy passes allowed files.
- [ ] Tests prove reliability policy fails plugin product files.
- [ ] Guard script exits 0 on pass and 1 on fail.
- [ ] DEVELOPMENT-WORKFLOW.md documents the guard before any local-main promotion.
- [ ] Flow validates and Obsidian evidence is updated.
- [ ] No files under `plugins/anyone-can-code/**` change.
## Done summary
Added tiny local promotion scope guard.

What changed:
- Added `scripts/check-promotion-scope.ps1`.
- Added unittest coverage in `tests/test_check_promotion_scope.py`.
- Added Flow spec/task `fn-3-automate-safe-local-promotion`.
- Added `development-system` policy so this guard can promote safely without broad allowances.
- Updated `AGENTS.md` and `DEVELOPMENT-WORKFLOW.md` to require the guard before local-main promotion.

What did not change:
- No plugin product files under `plugins/anyone-can-code/**` changed.
- No hook, MCP, runtime cache, marketplace, PR, push, tag, release, or online GitHub state changed.
## Evidence
- Commits: 4c474f9, 961f4ca, b1370cf
- Tests: python -m unittest tests.test_check_promotion_scope -> 3 OK after RED failures for missing script and missing development-system policy, python -m unittest discover -s tests -p test_*.py -> 3 OK, python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py -> 5 OK, python plugins\anyone-can-code\scripts\doctor.py --json -> 20 PASS, 0 WARN, 0 FAIL, python .flow\bin\flowctl.py validate --all --json -> valid, 3 specs, 10 tasks, 0 warnings, check-promotion-scope reliability 79216cd..a003412 -> PASS changed=12, check-promotion-scope reliability 79216cd..7994630 -> FAIL and listed plugin product files, check-promotion-scope development-system main..HEAD -> PASS changed=8
- PRs: