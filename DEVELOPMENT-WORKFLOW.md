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

1. Select or create one Linear issue.
2. Link it to one Flow-Next spec.
3. Develop in a `dev-*` worktree.
4. Run focused tests and commit locally.
5. Update `test-candidate` from the committed development branch.
6. Run full local validation in the testing worktree.
7. Fix failures in the development worktree, then test a new candidate.
8. Push the verified development branch to GitHub.
9. Open a pull request into `main`.
10. Merge only after checks and review pass.
11. Publish or release from stable `main`.
12. Mark the Linear issue done after verified merge/release evidence exists.

## Rules

- Never build features directly on `main`.
- Never publish from a development or testing worktree.
- Never edit product code in `test-candidate`.
- Never push secrets, local runtime state, or generated user data.
- A local commit is a checkpoint, not a release.
- A GitHub branch is a review candidate, not stable code.
- `main` is stable and release-ready.
- "Done" requires test evidence. "Published" requires GitHub merge/release evidence.

## Candidate Testing

From the main checkout, refresh the testing branch from a committed development branch:

```powershell
git -C ".worktrees\test-candidate" merge --ff-only dev-fn-1-define-project-direction-2
```

Then run project checks inside `.worktrees\test-candidate`.

If fast-forward is impossible, stop. Do not force, reset, or hide divergence.
