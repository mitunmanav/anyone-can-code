## Description
Build explicit Windows setup for storage-path selection, memory settings, optional viewer choice, and optional session-import source selection. Detect Obsidian. After clear user consent, offer official installation, official download page, or opening an already registered vault. Continue fully when declined or unavailable.

## Acceptance
- [x] Setup explains Markdown storage and viewer choices before execution.
- [x] User chooses or confirms storage path.
- [x] Setup asks before any session-file import and shows selected paths/scopes.
- [x] No-viewer path works fully.
- [x] Obsidian-present and Obsidian-absent paths both work.
- [x] Install uses an official source after explicit consent.
- [x] ACC does not bundle or redistribute Obsidian.
- [x] ACC does not silently accept package or source agreements.
- [x] Unsupported automatic vault registration falls back to visible manual “Open folder as vault” instructions.
- [x] Declined or failed installation does not block ACC.
- [x] No hidden download, launch, registry change, migration, move, or overwrite occurs.
- [x] Setup produces a plain-language receipt.

## Done summary
Built explicit portable Markdown setup with chosen storage path, no-viewer
default, optional consented Obsidian actions, preview-first scoped session
import, and plain-language setup receipts. Failed viewer setup remains
non-blocking. Invalid consent or scope fails before setup writes.
## Evidence
- Commits: local commit: Build explicit Markdown memory setup
- Tests: {'command': 'python -m unittest discover -s plugins\\anyone-can-code\\tests -p test_*.py', 'result': '43 tests OK'}, {'command': 'python -m py_compile plugins\\anyone-can-code\\scripts\\setup.py', 'result': 'passed'}, {'command': 'python plugins\\anyone-can-code\\scripts\\doctor.py --json', 'result': '24 PASS, 0 WARN, 0 FAIL'}, {'command': 'python .flow\\bin\\flowctl.py validate --all --json', 'result': 'valid, 5 specs, 17 tasks, 0 errors, 0 warnings'}, {'command': 'Flow Codex implementation review', 'result': 'blocked before execution by PermissionError WinError 5; no verdict claimed'}
- PRs: