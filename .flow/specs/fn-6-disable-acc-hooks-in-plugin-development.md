# fn-6-disable-acc-hooks-in-plugin-development Disable ACC hooks in plugin development tree

## Goal & Context
<!-- scope: business -->

Keep Anyone Can Code installed and usable while preventing only ACC lifecycle hooks from running anywhere under `C:\Users\Mitun Manav G Y\Desktop\Plugin development`. Other plugins and their hooks must remain enabled.

## Architecture & Data Models
<!-- scope: technical -->

Place a parent-tree marker at `.codex/anyone-can-code-hooks.disabled`. Add one shared hook-state helper that walks from the active repository/current directory toward filesystem root. Every ACC hook exits successfully with empty JSON before reads, writes, context injection, permission decisions, or memory learning when the marker is found. Remove the old project setting that disabled all Codex hooks.

## API Contracts
<!-- scope: technical -->

Marker contract: a file named `.codex/anyone-can-code-hooks.disabled` disables ACC hook behavior for its containing directory and all descendants. Disabled hook output is `{}` with exit code 0.

## Edge Cases & Constraints
<!-- scope: technical -->

The marker must affect root checkout, worktrees, inspiration repositories, and separate projects inside the Plugin development tree. It must not affect projects outside that tree. Missing or unreadable marker checks fail open without blocking Codex. ACC skills and MCP remain enabled.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** ACC hooks return empty success and create no ACC state when run below the marker.
- **R2:** ACC hooks retain normal behavior outside the marked tree.
- **R3:** Other Codex hooks remain enabled because project-wide `[features].hooks = false` is removed.
- **R4:** Marker, repo docs, Flow, and Obsidian record the scope and reason.
- **R5:** Tests, Doctor, Flow validation, and installed-cache verification pass.

## Boundaries
<!-- scope: business -->

Do not disable the ACC plugin, skills, or MCP. Do not disable Flow-Next or other plugin hooks. Do not change GitHub.

## Decision Context
<!-- scope: both -->

A project-wide Codex hook toggle is too broad. An ACC-owned marker checked by ACC hook scripts gives exact product-specific scope while preserving every other hook source.
