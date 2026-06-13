# fn-6-disable-acc-hooks-in-plugin-development.2 Handle repository-level plugin root

## Description
**Bug:** Codex Desktop can set `PLUGIN_ROOT` to the local marketplace repository root instead of the nested ACC plugin root.

ACC hook launch commands currently trust any non-empty plugin-root environment value. They then try to run `hooks/scripts/*.py` from the repository root and exit 1 before the ACC-only disable marker can be checked.

Fix root resolution so environment roots are accepted only when the expected hook script exists, or normalized to `plugins/anyone-can-code` when that nested plugin directory exists.
## Acceptance
- [ ] Regression test reproduces repository-level `PLUGIN_ROOT` and fails before implementation.
- [ ] Every ACC hook resolves the nested plugin root and returns exit 0 below the disable marker.
- [ ] Existing no-environment parent-workspace hook behavior remains green.
- [ ] Development and testing worktrees pass plugin tests, Doctor, and Flow validation.
- [ ] Repo docs, Flow evidence, and Obsidian project brain record the incident and fix.
- [ ] No GitHub action occurs.
## Done summary
Normalize repository-level plugin roots before launching ACC hook scripts; preserve ACC-only marker no-op behavior.
## Evidence
- Commits: 91051f4
- Tests: TDD RED: repository-level PLUGIN_ROOT produced three missing hook script failures, Focused GREEN: 2 tests OK, Full development plugin suite: 62 tests OK, Doctor: 26 PASS, 0 WARN, 0 FAIL, All six ACC hook events: exit 0, stdout {}, empty stderr
- PRs: