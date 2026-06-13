# fn-3-automate-safe-local-promotion Automate safe local promotion

## Goal & Context
<!-- scope: business -->

Non-technical user should not need to remember Git merge safety rules. A small local guard must prevent accidental whole-branch promotion into `main`, especially when development branches contain work outside the approved promotion scope.

## Architecture & Data Models
<!-- scope: technical -->

Add one lightweight PowerShell guard script under `scripts/check-promotion-scope.ps1`. The script reads Git diff file names between two refs and checks them against a named policy. It does not modify files, branches, remotes, Flow state, plugin runtime, hooks, skills, MCP config, marketplace config, or Obsidian.

Policy data is hardcoded in the script for now to keep the system small:

- `reliability`: allows Flow reliability files and workflow docs only.
- `development-system`: allows this guard script, its tests, `fn-3` Flow files, and workflow docs only.`n- `docs-only`: allows repo documentation and Flow documentation only.
- `plugin-product`: allows plugin product files, but is intentionally explicit and never used for reliability promotion.

## API Contracts
<!-- scope: technical -->

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check-promotion-scope.ps1 -Base <ref> -Candidate <ref> -Policy <policy>
```

Exit code `0` means every changed file is allowed by the policy. Exit code `1` means at least one changed file is forbidden or the script input is invalid. Output must include `PASS` or `FAIL` and list forbidden files on failure.

## Edge Cases & Constraints
<!-- scope: technical -->

The script must be cheap and local-only. It must not call GitHub or web APIs. It must not require Python packages, npm packages, or Flow internals. It must handle added, modified, deleted, and renamed files by checking the final path list from `git diff --name-only`.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** A local command exists that checks promotion scope before `main` receives candidate changes.
- **R2:** `reliability` policy fails when candidate diff includes `plugins/anyone-can-code/**`.
- **R3:** `reliability` policy passes when candidate diff includes only `fn-2` Flow reliability files plus `AGENTS.md` and `DEVELOPMENT-WORKFLOW.md`.
- **R4:** The guard is covered by tests that create temporary Git repos and verify pass/fail behavior.
- **R5:** Workflow docs require the guard before promoting candidate work into local `main`.
- **R6:** Flow and Obsidian record that this is a small guard, not a broad automation system.
- **R7:** No plugin runtime, hook, skill, MCP, cache, or marketplace files are changed by this spec.

## Boundaries
<!-- scope: business -->

Out of scope: automatic merging, pushing, PR updates, releases, background agents, remote GitHub mutation, changing ACC product behavior, or replacing human approval. This spec only adds a local red-light/green-light guard.

## Decision Context
<!-- scope: both -->

The earlier mistake happened because a whole development branch was merged into local `main` when only reliability files should have moved. A large promotion robot would add new failure paths. The safer first step is a tiny deterministic guard that makes the dangerous action visible and blocks it with a clear local failure.

