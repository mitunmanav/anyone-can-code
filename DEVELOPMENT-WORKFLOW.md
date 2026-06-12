# Development Workflow

This project separates tracking, development, testing, publishing, and release.

## Tool Roles

- Linear: product tracker. Holds priorities, ownership, and human-readable progress.
- Flow-Next: local engineering plan. Holds specs, tasks, dependencies, and evidence.
- Development worktree: feature implementation.
- Testing worktree: candidate validation only. Do not develop features here.
- Main checkout: stable publishing workspace.
- Local Git: records every safe checkpoint and commit.
- GitHub: stores reviewed branches, pull requests, stable `main`, and releases.

## Folder Roles

```text
anyone-can-code/
  main checkout                         stable and publishing
  .worktrees/dev-*                     development
  .worktrees/test-candidate            local testing
```

## Normal Flow

1. Search Linear project `Anyone Can Code` for the request.
2. Update the matching issue when it already exists; do not create a duplicate.
3. Create one Linear issue when no matching request exists.
4. Capture the full product request, decisions, additions, and corrections in that issue.
5. Link it to exactly one Flow-Next spec.
6. Treat Linear as continuity memory when chat/thread context is lost.
7. Edit product intent in Linear; reconcile it into Flow before more implementation.
8. Develop in a `dev-*` worktree.
9. Run focused tests and commit locally.
10. Update `test-candidate` from the committed development branch.
11. Run full local validation in the testing worktree.
12. Fix failures in the development worktree, then test a new candidate.
13. Push the verified development branch to GitHub for off-machine safety.
14. Open a pull request into `main`.
15. Merge only after checks and review pass.
16. Publish or release from stable `main`.
17. Mark the Linear issue done after verified merge/release evidence exists.

## Rules

- Never build features directly on `main`.
- Never publish from a development or testing worktree.
- Never edit product code in `test-candidate`.
- Never start implementation before searching Linear for an existing request.
- Never create a second Linear issue or Flow spec for the same product request.
- One Linear issue maps to one Flow spec; Flow tasks remain local.
- Product changes made in chat must also be written to the linked Linear issue.
- Product changes made in Linear must be reconciled before implementation resumes.
- Never push secrets, local runtime state, or generated user data.
- A local commit is a checkpoint, not a release.
- A pushed GitHub development branch is off-machine backup plus review candidate, not stable code.
- Testing branch stays local; do not push `test-candidate`.
- `main` is stable and release-ready.
- "Done" requires test evidence. "Published" requires GitHub merge/release evidence.

## Candidate Testing

From the main checkout, refresh the testing branch from a committed development branch:

```powershell
git -C ".worktrees\test-candidate" merge --no-edit dev-fn-1-define-project-direction-2
```

Then run project checks inside `.worktrees\test-candidate`. Testing branch may
contain candidate merge commits; it is never published.

If Git reports a conflict, stop. Resolve candidate history in development first.
Do not force, reset, or hide divergence.
