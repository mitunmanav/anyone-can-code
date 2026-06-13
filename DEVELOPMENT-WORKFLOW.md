# Development Workflow

This project separates tracking, development, testing, publishing, and release.

## Tool Roles

- Obsidian: permanent linked project brain. Holds requests, ideas, decisions,
  additions, updates, deletions, causes, reasons, progress, test results, Git
  history, release evidence, and important links.
- Flow-Next: local engineering plan. Holds specs, tasks, dependencies, and evidence.
- Development worktree: feature implementation.
- Testing worktree: candidate validation only. Do not develop features here.
- Main checkout: stable publishing workspace.
- Local Git: records every safe checkpoint and commit.
- GitHub: stores stable `main` and releases after explicit user command.

## Obsidian Structure

- `00 ACC Home`: project hub and graph center.
- `01 Product Direction`: durable goal, user, modules, constraints, and scope.
- `02 Current Status`: current tasks, worktrees, GitHub state, and verification.
- `03 Timeline`: chronological history.
- `04 Decisions`: accepted rules and reasons.
- `05 Development Workflow`: local delivery process.
- `06 Task Map`: human-readable mirror of Flow tasks and dependencies.
- `07 Evidence and Verification`: tests, failures, warnings, and uncertainty.
- `08 Git and Release History`: commits, tags, PR state, and releases.
- `09 Linear Migration Archive`: legacy migration record only.

Obsidian does not replace Flow mechanics. Obsidian explains product history and
decisions. Flow owns technical task state.

## Folder Roles

```text
anyone-can-code/
  main checkout                         stable and publishing
  .worktrees/dev-*                     development
  .worktrees/test-candidate            local testing
```

## Normal Flow

1. Open `I:\Obsidian vaults\Projects\Anyone Can Code\00 ACC Home.md`.
2. Search connected ACC notes for the request or decision.
3. Update the matching note instead of creating duplicate knowledge.
4. Add a new linked note only when the concept is genuinely separate.
5. Record what changed, why, and links to affected tasks or evidence.
6. Update Flow when technical requirements or tasks changed.
7. Treat Obsidian as continuity memory when chat/thread context is lost.
8. Mirror Flow task status in `06 Task Map` and `02 Current Status`.
9. Reconcile product intent into Flow before more implementation.
10. Develop in a `dev-*` worktree.
11. Run focused tests and commit locally.
12. Update `test-candidate` from the committed development branch.
13. Run full local validation in the testing worktree.
14. Fix failures in the development worktree, then test a new candidate.
15. On user approval, run the scoped promotion guard before local `main` changes.
16. Promote only the approved file scope into local `main`; do not merge a
    whole development branch unless the guard policy explicitly allows every
    changed file.
17. Keep local `main` offline until the user explicitly orders a GitHub action.
18. On explicit user command, push verified local `main` to GitHub.
19. On explicit user command, publish or release from stable `main`.
20. Update Obsidian status, timeline, and evidence after completion or publication.

## Development Reliability Gate

Before changing anything, classify the work:

- `development-system`: Flow, repo workflow docs, Obsidian, worktree process,
  verification rules, cache handling, or delivery policy.
- `plugin-product`: ACC runtime behavior, skills, hooks, MCP server, assets,
  setup scripts, Doctor behavior, or user-facing plugin features.

For development-system work, do not edit `plugins/anyone-can-code/**` unless the
user explicitly expands scope. Use Flow-Next as the technical control plane and
Obsidian as the history/evidence brain.

### Pre-work gate

Run this before editing:

1. Read `AGENTS.md`.
2. Read Obsidian `00 ACC Home`, `02 Current Status`, and any affected notes.
3. Run `python .flow\bin\flowctl.py ready --spec <spec-id>`.
4. Check `git status --short --branch` in root, dev, and test worktrees.
5. State whether work is `development-system` or `plugin-product`.
6. State which files are allowed to change.

### Change-impact matrix

| Change type | Required updates | Required proof |
|---|---|---|
| Flow spec/task | Flow task/spec via `python .flow\bin\flowctl.py`; Obsidian status/evidence/task map if current state changes | `python .flow\bin\flowctl.py validate --all`; ready/task output |
| Repo workflow docs | Obsidian decision/status/evidence if process meaning changes | doc diff; Obsidian link check |
| Obsidian project brain | Related Obsidian notes; Flow only if technical requirements/tasks change | note count/link check; status consistency scan |
| Plugin source or hook behavior | Tests, Doctor, runtime cache check, Flow evidence, Obsidian evidence, repo docs if workflow/setup changed | tests pass; Doctor pass; cache source/hash or behavior proof |
| Runtime cache | Obsidian evidence; source remains authoritative | source/cache hash or behavior proof; no source drift |
| Worktree sync/merge | Obsidian status/evidence/git ledger; Flow if task state changed | root/dev/test status and hashes; candidate validation |
| GitHub/remote | Obsidian git ledger/evidence/status | exact user command; remote ref proof; no-push proof otherwise |

### Pre-done gate

Do not call work complete until all applicable checks pass:

1. `python .flow\bin\flowctl.py validate --all`
2. Relevant tests and Doctor for touched area.
3. Obsidian note count and broken-link check.
4. Root/dev/test `git status --short --branch`.
5. Current root/dev/test commit hashes.
6. Runtime cache check when plugin source or hooks changed.
7. `git ls-remote origin refs/heads/main` when GitHub state matters.
8. Flow evidence and Obsidian evidence updated.

### Local-main promotion guard

Before local `main` receives candidate work, run the scope guard from the root
checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check-promotion-scope.ps1 -Base main -Candidate <candidate-branch> -Policy <policy>
```

Use `-Policy reliability` for development reliability work. If the guard prints
`FAIL`, stop. Do not merge, cherry-pick, copy files, push, or publish until the
forbidden files are understood and the user approves the expanded scope.

The guard is intentionally small. It only reads Git diff file names and exits
with pass/fail. It does not change files, branches, Flow state, Obsidian,
runtime cache, GitHub, PRs, tags, releases, or plugin behavior.

### Evidence receipt

Every completed reliability or plugin task should leave this proof shape in Flow
evidence and Obsidian:

```text
What changed:
What did not change:
Files touched by category:
Commands run:
Results:
Root/dev/test hashes:
Runtime cache status:
GitHub mutation status:
Remaining risk:
Next task:
```

## Rules

- ACC hook scripts must return empty success before reads, writes, context
  injection, permission decisions, or learning anywhere below a parent
  `.codex/anyone-can-code-hooks.disabled` marker.
- ACC hook launchers must validate `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT`.
  Codex may supply the marketplace repository root, so launchers must normalize
  that value to nested `plugins/anyone-can-code` before running hook scripts.
- The parent `Plugin development` tree carries that marker. Do not use
  `[features].hooks = false` for ACC isolation because that disables unrelated
  hooks too.
- Never build features directly on `main`.
- Never merge a whole development branch into local `main` without first running
  `scripts\check-promotion-scope.ps1` and confirming the selected policy allows
  every changed file.
- Never publish from a development or testing worktree.
- Never edit product code in `test-candidate`.
- Never start implementation before searching connected ACC Obsidian notes.
- Never create duplicate Obsidian notes or Flow specs for the same product request.
- Keep Flow technical details in Flow; keep durable project meaning in Obsidian.
- Product changes made in chat must also be written to connected ACC notes.
- Product changes made in Obsidian must be reconciled into Flow before implementation resumes.
- Record what changed, what was deleted, what failed, what was added, why it
  happened, decisions made, alternatives rejected, and evidence in Obsidian.
- Never erase history to make notes look clean. Record reversals, superseded
  decisions, and reasons so graph history remains understandable.
- Never push secrets, local runtime state, or generated user data.
- A local commit is a checkpoint, not a release.
- Never run `git push`, create/update a PR, merge, tag, publish, or release unless
  the user explicitly commands that exact online action.
- GitHub safety backup is recommended, but permission is per push.
- Push verified local `main` only, unless the user explicitly requests another branch.
- Development and testing branches stay local.
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

From the main checkout, refresh the testing branch from the current committed
development branch:

```powershell
$developmentWorktrees = @(Get-ChildItem ".worktrees" -Directory -Filter "dev-*")
if ($developmentWorktrees.Count -ne 1) { throw "Expected exactly one development worktree." }
$developmentBranch = git -C $developmentWorktrees[0].FullName branch --show-current
git -C ".worktrees\test-candidate" merge --no-edit $developmentBranch
```

Then run project checks inside `.worktrees\test-candidate`. Testing branch may
contain candidate merge commits; it is never published.

If Git reports a conflict, stop. Resolve candidate history in development first.
Do not force, reset, or hide divergence.

After validation passes, wait for user approval before merging the development
branch into the root local `main`. Pushing local `main` online requires a
separate explicit command.
