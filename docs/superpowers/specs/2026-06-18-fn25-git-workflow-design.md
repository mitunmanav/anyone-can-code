# fn-25 ACC Core Git Workflow Design

Date: 2026-06-18  
Spec: fn-25-build-acc-core-everything-workflow-from  
Status: approved for implementation  
Approved by: user (2026-06-18)

## Problem

Zenfit runtime trial proved ACC had no built-in git workflow. Each project had to
build its own git manager workaround. ACC must absorb this as a native owned
workflow so no project ever needs to do it again.

## Goal

ACC owns git: worktrees, branches, commits, merge, push, and PR. Automatic by
default. Manual mode switchable at setup.

## Inspiration

Pattern adapted from superpowers `finishing-a-development-branch` skill.  
Credit: claude-plugins-official/superpowers  
Original pattern: verify tests → detect environment → execute → clean up

ACC adaptation adds:
- full-auto mode with manual toggle at setup
- canonical state receipts after every git action
- circuit breaker on git failure
- compaction re-anchor recovery

Credit lives in repo CREDITS.md only. Not in code files.

## Core pipeline (auto mode)

```
1. ACC begin task
   → create worktree: .worktrees/acc/<task-slug>-<YYYYMMDD>
   → branch: acc/<task-slug>-<YYYYMMDD>

2. ACC work in worktree
   → edits, builds, runs tests

3. Tests pass → ACC commit
   → atomic commits (one concern per commit)
   → conventional commits format: feat/fix/chore
   → AI context in commit body (not subject)
   → never commit broken code — test gate is mandatory

4. ACC merge to main
   → verify tests on merged result (superpowers rule)
   → merge only if green

5. ACC remove worktree
   → cd to main repo root first (superpowers hard rule)
   → only remove worktrees under .worktrees/ (provenance check)
   → git worktree prune after

6. ACC push + create PR (if remote configured)
   → PR body = task summary + evidence receipt link

7. ACC write canonical state receipt
   → what committed, what tested, what pushed, PR link, verification level
```

## Manual mode

Same steps. ACC pauses before step 3 (commit), step 4 (merge), and step 6
(push/PR). Shows plan. Waits for approval.

## Setup toggle

```yaml
# In ACC preferences — set during acc-setup
git_mode: auto      # default
git_mode: manual    # ACC pauses before each destructive git action
```

Doctor checks this setting exists and is valid.

## Safety gates

| Gate | Rule |
|---|---|
| Tests must pass | Never commit broken code. Period. |
| Provenance check | Only remove worktrees ACC created (under .worktrees/) |
| cd to main root | Before any worktree remove |
| Circuit breaker | 2 git failures → stop, write skip receipt, report |
| No force push | Never. Even in auto mode. |
| Push/PR approval | Always requires explicit user approval even in auto mode |
| Discard = typed confirm | Must type "discard" — no accident |

## fn-25 task mapping

| Task | What |
|---|---|
| .1 | Mandatory session audit checklist preflight |
| .2 | This spec — built-in safe git workflow contract |
| .3 | Implement ACC core safe git workflow (scripts/git_workflow.py) |
| .4 | Record workflow evidence in canonical ACC state |
| .5 | Make learning evidence provable |
| .6 | Compaction and abort re-anchor recovery |

## Files to create/modify

- `plugins/anyone-can-code/scripts/git_workflow.py` — new, core git workflow
- `plugins/anyone-can-code/plugins/anyone-can-code/ORCHESTRATOR.md` — add git_workflow route
- `plugins/anyone-can-code/plugins/anyone-can-code/SETUP.md` — add git_mode preference
- `plugins/anyone-can-code/scripts/canonical_state.py` — add git receipt fields
- `CREDITS.md` — superpowers credit (repo root)
- `README.md` — acknowledgment section

## Verification

- Focused git workflow tests pass
- Full plugin tests pass
- Doctor includes git_workflow check
- Flow validation passes
- diff check passes

## Boundary

- No GitHub push during implementation
- No change to hook scripts
- No change to guard.py or state.py
- Changes go to development worktree only until tested
