# fn-15-resolve-active-acc-project-before-state.1 Discover and enforce active ACC project selection

## Description
Build a shared bounded project resolver for core ACC state operations. Reproduce the June 14 failure: workspace root contains fresh/idle ACC state while one nested project contains meaningful active state and memory. Integrate resolution before setup/update writes and require help/status/resume to resolve state root before reading.
## Acceptance
- [ ] One active nested ACC project is selected over idle root state.
- [ ] Root state remains selected when it is meaningfully active.
- [ ] Multiple plausible active projects block with explicit candidates.
- [ ] Discovery is bounded and excludes generated/cache directories.
- [ ] Setup/update resolve before creating or replacing state.
- [ ] Help/status/resume guidance requires resolver output.
- [ ] Doctor reports selected, root, nested, or ambiguous state.
- [ ] Regression tests, full tests, compile, Doctor, and Flow validation pass.
- [ ] Repo docs and Obsidian brain are updated.
## Done summary
Implemented shared bounded active-project resolution for core ACC state operations. Setup and update resolve before state access. Help, status, and resume require the resolver. Doctor reports requested, nested-selected, or ambiguous state. Meaningful nested state outranks idle workspace-root state. Multiple plausible projects block. Generated/cache folders, .worktrees, and symlinks are excluded.
## Evidence
- Commits:
- Tests: 10 focused project-resolution regression tests passed, 104 full plugin tests passed, Python compileall passed, Doctor 34 PASS, 0 WARN, 0 FAIL, Flow validation 0 errors, 0 warnings, git diff --check passed
- PRs: