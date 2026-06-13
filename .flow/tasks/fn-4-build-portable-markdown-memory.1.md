## Description
Lock portable linked-Markdown storage, viewer choices, consent boundaries, path rules, note schema, existing-session import rules, settings, and recovery behavior before implementation.

Viewer choices:

- none: store linked Markdown and continue;
- Obsidian: optional third-party viewer through explicit official install/open flow;
- ACC viewer: future work, unavailable in this release.

## Acceptance
- [x] Markdown storage works without any viewer.
- [x] Default storage path is proposed, displayed, and changeable.
- [x] User can explicitly select no viewer.
- [x] Obsidian is labeled optional third-party software.
- [x] ACC viewer is recorded as future work, not promised as available.
- [x] Every download, launch, agreement, migration, move, and overwrite boundary has explicit consent text.
- [x] Markdown note schema supports links and project, user, shared, lesson, failure, decision, evidence, and archive records.
- [x] Existing local session file import contract covers explicit source choice, provenance, backup, deduplication, scope labels, and receipt.
- [x] Settings contract covers memory path, viewer mode, import sources, import scope, and production-repo caution.
- [x] Maintainer vault and end-user memory are separate.
- [x] No Obsidian binary or installer redistribution is planned.

## Done summary
Defined portable Markdown memory contract, setup defaults, viewer/import consent rules, and updated docs/tests for portable-markdown mode.
## Evidence
- Commits: local commit: Define portable Markdown memory contract
- Tests: {'result': '29 tests OK', 'command': 'python -m unittest discover -s plugins\\anyone-can-code\\tests -p test_*.py'}, {'result': '24 PASS, 0 WARN, 0 FAIL', 'command': 'python plugins\\anyone-can-code\\scripts\\doctor.py --json'}, {'result': 'valid, 5 specs, 17 tasks, 0 errors, 0 warnings', 'command': 'python .flow\\bin\\flowctl.py validate --all --json'}
- PRs: