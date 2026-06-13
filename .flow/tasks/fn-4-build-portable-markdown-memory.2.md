## Description
Replace JSONL as the primary durable learning store with Markdown notes. Keep the bundled MCP interface, top 3-5 retrieval, advisory-memory rule, existing-session import pipeline, and optional rebuildable search index.

## Acceptance
- [x] Store and retrieve project, user, and shared Markdown memories.
- [x] Notes are readable without ACC or Obsidian.
- [x] User-selected existing session files convert into scoped Markdown notes with provenance.
- [x] Retrieval stays capped at 3-5.
- [x] Duplicate and weak lessons are bounded.
- [x] Search index can be deleted and rebuilt from Markdown.
- [x] Secrets are rejected or redacted.

## Done summary
Built portable Markdown MCP memory backend with readable notes, top-5 retrieval, dedupe, rebuildable index, explicit session-file import receipts, project isolation, and secret redaction.

## Evidence
- Commits: local commit `Build portable Markdown memory backend`
- Tests:
  - `python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py` -> 35 tests OK
  - `python plugins\anyone-can-code\scripts\doctor.py --json` -> 24 PASS, 0 WARN, 0 FAIL
  - `python .flow\bin\flowctl.py validate --all --json` -> valid, 5 specs, 17 tasks, 0 errors, 0 warnings
  - MCP stdio smoke -> store/retrieve returned `portable-markdown` and count 1
- PRs: none
