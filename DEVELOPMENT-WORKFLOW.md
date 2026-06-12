# Development Workflow

This project separates tracking, development, testing, publishing, and release.

## Tool Roles

- Obsidian: complete project brain and history. Holds requests, decisions, history, explanations, evidence, and continuity.
- Flow-Next: local technical plan. Holds specs, tasks, dependencies, and task evidence.
- Development worktree: feature implementation.
- Testing worktree: candidate validation only. Do not develop features here.
- Main checkout: stable publishing workspace.
- Local Git: records every safe checkpoint and commit.
- GitHub: stores reviewed branches, pull requests, stable `main`, and releases. Online `main` is updated only by explicit command and should match local `main`.
- Linear: legacy archive only unless the user explicitly re-enables it.

## Folder Roles

```text
anyone-can-code/
  main checkout                         stable and publishing
  .worktrees/dev-*                     development
  .worktrees/test-candidate            local testing
```

## Normal Flow

1. Read Obsidian project home for current truth.
2. Capture product requests, decisions, additions, and corrections in Obsidian.
3. Create or update exactly one Flow-Next spec when the request affects technical work.
4. Treat Obsidian as continuity memory when chat/thread context is lost.
5. Reconcile Obsidian requirement changes into Flow before more implementation.
6. Re-anchor on Flow spec and task state before coding.
7. Keep Flow focused on technical task state, not project history.
8. Develop in a `dev-*` worktree.
9. Run focused tests and commit locally.
10. Update `test-candidate` from the committed development branch.
11. Run full local validation in the testing worktree.
12. Fix failures in the development worktree, then test a new candidate.
13. Push the verified development branch to GitHub for off-machine safety.
14. Open a pull request into `main` only when explicitly requested.
15. Merge only after checks and review pass.
16. Keep local `main` as the approved clean source.
17. Push local `main` to online GitHub `main` only after an explicit command.
18. Record verified merge/release evidence in Obsidian and Flow task evidence.

## Rules

- Never build features directly on `main`.
- Never publish from a development or testing worktree.
- Never edit product code in `test-candidate`.
- Never start implementation before reading current Obsidian and Flow context.
- Never create a second Flow spec for the same technical request.
- Product changes made in chat must also be written to Obsidian.
- Product changes made in Obsidian must be reconciled into Flow before implementation resumes.
- Never push secrets, local runtime state, or generated user data.
- A local commit is a checkpoint, not a release.
- A pushed GitHub development branch is off-machine backup plus review candidate, not stable code.
- Testing branch stays local; do not push `test-candidate`.
- `main` is stable and release-ready.
- Online GitHub `main` must be an exact copy of local `main`, and only after the user commands a push.
- "Done" requires test evidence. "Published" requires GitHub merge/release evidence.
- For ACC plugin development, read Obsidian project/docs memory first. The vault folder `official-codex-docs` has an index file for scraped Codex docs.
- If local official docs are outdated, missing, or contradict observed behavior, verify against the web and record that reason in Obsidian.
- Use inspiration repos only as reference material. Put cloned references under `C:\Users\Mitun Manav G Y\Desktop\Plugin development\inspiration`.
- Use codegraph MCP for efficient repo/code navigation. Fall back to targeted `rg` and file reads only for files codegraph does not cover.
- Never load full repos, full docs folders, or large raw files into chat context. Keep context sliced, summarized, and path-cited.
- Any code, config, workflow, setup, task, or decision change must update all affected docs automatically in the same work session.
- Obsidian must be updated immediately with agent actions, decisions, outcomes, non-actions, evidence, warnings, and next state.

## Candidate Testing

From the main checkout, refresh the testing branch from a committed development branch:

```powershell
git -C ".worktrees\test-candidate" merge --no-edit dev-fn-1-define-project-direction-2
```

Then run project checks inside `.worktrees\test-candidate`. Testing branch may
contain candidate merge commits; it is never published.

If Git reports a conflict, stop. Resolve candidate history in development first.
Do not force, reset, or hide divergence.
