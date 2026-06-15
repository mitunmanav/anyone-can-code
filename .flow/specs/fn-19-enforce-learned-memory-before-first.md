# fn-19-enforce-learned-memory-before-first Enforce learned memory before first action

## Overview
ACC must not rely on passive memory docs. After setup, update, restart, or new
thread, the front door must analyze the request, resolve the active project,
retrieve relevant learned mistakes/preferences from the selected portable
Markdown memory path, and show whether memory was used before first meaningful
action.

## Scope
- Add route contract requiring memory preflight.
- Add executable source helper for store/retrieve proof.
- Preserve selected project memory path.
- Require visible `Relevant memory used: ...` output.
- Cover first questions, planning, specialist routing, browser/server actions,
  and tool actions.
- Update docs, Doctor, tests, and Obsidian.

## Approach
- Use existing portable Markdown memory backend, not a new store.
- Read project memory path from ACC preferences.
- Keep memory advisory; it cannot grant permission or claim truth.
- Add focused regression tests for route contract and post-setup/update recall.

## Quick commands
<!-- Required: at least one smoke command for the repo -->
- `python -m unittest plugins.anyone-can-code.tests.test_memory_preflight`
- `python -m unittest plugins.anyone-can-code.tests.test_front_door`
- `python plugins/anyone-can-code/scripts/doctor.py --json`

## Acceptance
- [ ] Front door returns `memory_preflight` for every route and requirement change.
- [ ] Memory preflight uses selected project memory path from preferences.
- [ ] Learned mistake stored before setup/update rerun is retrieved after rerun.
- [ ] Orchestrator docs require visible `Relevant memory used: ...` before first action.
- [ ] Doctor reports memory preflight health.
- [ ] Full tests, compile, Doctor, and Flow validation pass.

## References
- [[43 FN-19 Learned Memory Preflight 2026-06-15]]

## Installed Runtime Evidence 2026-06-15

- Backed up and refreshed both local ACC installed cache roots for installed
  proof only.
- Safety receipt:
  `.codex/anyone-can-code/artifacts/receipts/20260615T064929Z-refresh-installed-ACC-cache-from-local-source-for-installed-proof-c7ee888e.json`.
- Installed QA receipt:
  `.codex/anyone-can-code/artifacts/installed-qa/installed-qa-20260615T064937Z-e8fb67b8.json`.
- `memory_write_through` scenario passed for store, setup, update, and
  new-thread recall before first action.
- No remote action occurred.
