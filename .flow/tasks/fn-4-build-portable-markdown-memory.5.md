## Description
Verify portable Markdown memory and all optional-viewer paths in testing worktree using fresh and upgraded projects.

## Acceptance
- [ ] Fresh setup with no viewer passes.
- [ ] Fresh setup with Obsidian already installed passes.
- [ ] Obsidian missing plus install declined passes.
- [ ] Obsidian installation failure preserves usable Markdown setup.
- [ ] Official download-page choice works without forced installation.
- [ ] Manual “Open folder as vault” instructions are accurate.
- [ ] Custom storage path passes.
- [ ] Existing folder and file conflicts do not overwrite silently.
- [ ] Permission denial and migration failure preserve rollback.
- [ ] JSONL-to-Markdown migration is complete and deduplicated.
- [ ] Existing-session import is complete, scoped, deduplicated, and receipt-backed.
- [ ] Another plain file reader can understand stored memory and links.
- [ ] Doctor separates storage health from optional viewer availability.
- [ ] Doctor, tests, Flow validation, and promotion guard pass.

## Done summary
Verified fresh setup, optional Obsidian choices, rollback safety, migration
dedupe, selected-session receipts, plain-reader links, Doctor separation, Flow
validity, and promotion scope in development and testing.
## Evidence
- Commits: 1aab2ec
- Tests: 56 plugin unittest tests pass in development and testing, 4 promotion guard tests pass, Python compile passes, Doctor 26 PASS, 0 WARN, 0 FAIL after testing setup repair, Flow validates: 5 specs, 17 tasks, 0 errors, 0 warnings, plugin-product promotion guard passes
- PRs: