# Resolve active ACC project before state operations

## Problem

Codex Desktop can open a non-Git workspace root while the real ACC project is nested below it. ACC setup/update created fresh root state and help/status trusted it, while active nested state and memory remained under `zenfit-site`.

## Requirements

- R1: Before setup, update, help, status, or resume trusts workspace-root state, discover bounded nested ACC project candidates.
- R2: Prefer current root only when it has meaningful active state or no nested ACC state exists.
- R3: If exactly one nested ACC project has meaningful state, select it and report selected path.
- R4: If multiple plausible active projects exist, block and ask user; never guess or overwrite.
- R5: Discovery must be bounded, ignore common generated/cache folders, and avoid recursive whole-disk scans.
- R6: Setup/update must not create or replace root state before resolution.
- R7: Project selection is core ACC behavior, separate from deferred hook resolution in fn-14.
- R8: Preserve Plugin development ACC disable rules and do not run ACC runtime/hooks here.

## Scope

Build one shared resolver, integrate it into setup/update and user-facing help/status/resume guidance, add Doctor visibility, tests, docs, Flow evidence, and Obsidian record.

## Out of Scope

Hook lifecycle receipts and non-Git hook execution remain fn-14. No installed runtime mutation, GitHub action, or source session modification.

## Verification

Test root-only, one active nested project, idle root versus active nested project, multiple active nested projects, bounded exclusions, setup/update pre-write behavior, Doctor summary, full tests, compile, and Flow validation.

## Decision Context

Selected shared bounded resolver. Rejected help-only fix because update could still create conflicting state. Rejected unrestricted recursion because it can be slow and choose unrelated projects.
