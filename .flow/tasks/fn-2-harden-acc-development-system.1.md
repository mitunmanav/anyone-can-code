# fn-2-harden-acc-development-system.1 Define change-impact matrix

## Description
﻿Define the compact matrix that tells agents what must be updated when a change type happens. Keep it development-system focused and plugin-source neutral.

Required change types:
- Plugin source/hook behavior
- Flow spec/task state
- Obsidian project brain
- Repo workflow docs
- Runtime cache
- Worktree sync/merge
- GitHub/remote state
## Acceptance
﻿- [ ] Matrix exists in repo workflow docs and/or Obsidian.
- [ ] Each change type lists required Flow, Obsidian, repo docs, tests, cache, worktree, and GitHub proof.
- [ ] Matrix says plugin files are not changed by this reliability setup.
- [ ] Flow validates after updates.
## Done summary
Defined change-impact matrix in DEVELOPMENT-WORKFLOW.md and Obsidian 19 Development Reliability System. No plugin source files changed.
## Evidence
- Commits:
- Tests:
- PRs: