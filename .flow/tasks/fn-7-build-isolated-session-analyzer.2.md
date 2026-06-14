---
satisfies: [R2, R4, R5, R6, R7]
---

## Description
Replace arbitrary explicit input paths with one fixed manual inbox at `C:\Users\Mitun Manav G Y\Desktop\SESSION ANALYSER MD FILES`.

**Size:** S
**Files:** sibling `session-analyzer/**`; Flow evidence; Obsidian architecture notes.

## Approach
- Python enumerates only direct `*.md` files in fixed inbox.
- No recursive search and no caller-supplied input path option.
- Empty inbox fails clearly without creating a dump run.

## Acceptance
- [ ] Manual command needs no file paths.
- [ ] Only direct `.md` files from exact inbox are read.
- [ ] Subfolders, non-Markdown files, and all other locations are ignored.
- [ ] Empty/missing inbox fails without output.
- [ ] Tests and docs reflect fixed inbox.
- [ ] Existing safety boundaries remain green.
- [ ] No real session files analyzed during this change.

## Done summary
Changed analyzer to one fixed manual inbox:
`C:\Users\Mitun Manav G Y\Desktop\SESSION ANALYSER MD FILES`.
User-facing command accepts no input paths. Runtime reads only direct `.md`
files, never recurses, ignores other file types, and fails on missing/empty
inbox. Existing output and ACC isolation boundaries remain unchanged.
## Evidence
- Commits:
- Tests: python -m unittest discover -s tests -v: 9 tests OK, python -m py_compile session_analyzer.py: pass, PowerShell run.ps1 syntax: pass, Fixed inbox direct listing: 2 .md files detected, contents not analyzed, No new ACC plugin source changes
- PRs: