# fn-21-guard-windows-command-execution-in-acc Guard Windows command execution in ACC guidance

## Goal & Context
<!-- scope: business -->

Raw session audit found ACC-guided work still produced avoidable Windows command failures:

- `npm.ps1` blocked by PowerShell execution policy.
- Bash `||` failed in PowerShell.
- Git ran from a non-repo root.

ACC must guide and guard command execution for Windows users before tool work starts. The goal is not to execute commands for the user; it is to make ACC's own plans, specialist routing, and verification guidance avoid known Windows shell traps.

## Architecture & Data Models
<!-- scope: technical -->

Add a small Windows command guard to the ACC front-door/orchestration contract. It should produce structured guidance that downstream ACC docs and specialist handoffs must preserve:

- shell family: PowerShell on Windows unless proven otherwise;
- package-manager binary preference: `npm.cmd` over `npm` in PowerShell when execution policy can intercept `npm.ps1`;
- shell operator guard: avoid Bash-only operators such as `||` in PowerShell guidance;
- git root guard: resolve and use the active project/repo root before any Git command, and report when no repo root is available;
- evidence wording: failed commands stay visible as failures, not hidden retries.

The guard should live near existing front-door/status/orchestration contracts so every route can reference it before browser/server/tool work.

## API Contracts
<!-- scope: technical -->

ACC route metadata exposes a `command_guard` object with at least:

- `shell`: expected shell family for guidance;
- `windows`: boolean;
- `package_runner`: preferred command token for npm-family commands on Windows;
- `forbidden_patterns`: user-facing list of shell patterns to avoid;
- `cwd_rule`: repo-root rule for Git and project commands;
- `failure_policy`: how to report and recover from command failures.

Skill docs that execute or guide commands must require this contract before command/tool work.

## Edge Cases & Constraints
<!-- scope: technical -->

- Plugin development keeps ACC disabled as helper while this is built.
- Do not depend on Session Analyzer runtime; use the audit findings as evidence only.
- Do not mutate remotes or old branches.
- Do not hide failed command attempts.
- Preserve non-Windows behavior.
- Preserve existing active-project resolution from `fn-15`.
- If shell family is unknown, prefer a safe explicit command form and ask/inspect before risky command syntax.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** Tests prove Windows command guard prefers `npm.cmd` over `npm` in PowerShell guidance.
- **R2:** Tests prove Bash-only `||` is rejected or rewritten for PowerShell guidance.
- **R3:** Tests prove Git command guidance requires a resolved repository root and does not run from the saved workspace parent by default.
- **R4:** Front-door/orchestrator/bridge docs require command guard before shell, server, browser, package-manager, or Git work.
- **R5:** Doctor or verification docs expose the command guard so absence/regression is visible.
- **R6:** Raw audit failures are recorded in Obsidian and Flow evidence.
- **R7:** Existing tests, compile, Doctor, and Flow validation pass.

## Boundaries
<!-- scope: business -->

Out of scope:

- A full shell parser.
- Replacing Codex tool execution.
- Running Session Analyzer.
- Changing Git remotes, pushing, opening PRs, tagging, publishing, or releasing.
- Disabling all hooks or broad plugin behavior.

## Decision Context
<!-- scope: both -->

The audit failures are simple and preventable. A narrow command guard is enough: it turns known Windows traps into explicit route metadata and docs requirements. This fits ACC's current architecture because prior repairs already added front-door contracts for visible responses, memory preflight, specialist accounting, and evidence claims.
