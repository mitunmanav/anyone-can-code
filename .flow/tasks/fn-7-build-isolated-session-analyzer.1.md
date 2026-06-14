---
satisfies: [R1, R2, R3, R4, R5, R6, R7, R8]
---

## Description
Build isolated manual analyzer, safety guards, mechanical extraction, sanitized dump artifacts, saved interpretation prompt, tests, and Obsidian documentation.

**Size:** M
**Files:** sibling `session-analyzer/**`; Flow evidence only under `.flow/**`; Obsidian dump/brain notes.

## Approach
- Use Python standard library only.
- Resolve and validate every path before reading or writing.
- Create output through one allowlisted dump-root function.
- Keep interpretation manual and separate from extraction.

## Investigation targets
**Required:**
- `AGENTS.md`
- `../AGENTS.md`
- `.flow/templates/spec.md`
- Obsidian notes 23-26
- `offical-codex-docs/index.md`

## Acceptance
- [ ] Tests prove normal manual run.
- [ ] Tests prove protected inputs rejected.
- [ ] Tests prove output escape and overwrite rejected.
- [ ] Tests prove malformed records reported without source mutation.
- [ ] Generated dump contains required artifacts and redaction.
- [ ] ACC repo source, configs, hooks, worktrees, and runtime remain untouched.
- [ ] Obsidian records safe workflow and promotion gate.
- [ ] Flow validates; GitHub untouched.

## Done summary
Built isolated manual session analyzer outside ACC repo. Added fixed Obsidian
dump boundary, protected-input rejection, immutable run folders, checksummed
facts, sanitized evidence, saved analysis prompt, tests, and Obsidian
architecture records. No real session export analyzed. ACC source/runtime,
configs, hooks, worktrees, Git, and GitHub untouched.
## Evidence
- Commits:
- Tests: python -m unittest discover -s tests -v: 6 tests OK, python -m py_compile session_analyzer.py: pass, PowerShell run.ps1 syntax: pass, flowctl validate --spec fn-7-build-isolated-session-analyzer: valid, 0 errors, 0 warnings, git status confirms no ACC plugin source changes from analyzer work
- PRs: