# fn-25 Build ACC core everything workflow from real use

## Goal & Context
<!-- scope: business -->

ACC's product goal is that a non-technical user describes what they want, answers only necessary questions, and ACC manages the project workflow end-to-end with evidence. The Zenfit runtime session proved ACC has useful guardrails, but not the complete machinery for this promise.

Real-use evidence is recorded in Obsidian:

- [[46 Zenfit ACC Runtime Trial 2026-06-16]]
- [[47 Zenfit ACC Runtime Deep Audit 2026-06-16]]
- Prior audit/checklist sources: [[23 Session Audit Master]], [[30 Session Analyzer Extraction Capability Map]], [[36 Manual Usage Session Audit 2026-06-14]]

The key failure was not that a git manager was built. The key failure was that ACC did not already own that capability as plugin core. It built `zenfit-site/scripts/git_manager/` in a normal project because ACC had policy but not built-in machinery for routine safe git workflow.

This spec turns that real-use gap back into Plugin development work.

## Architecture & Data Models
<!-- scope: technical -->

Build ACC core support for routine project workflow automation rather than expecting each project to grow its own manager.

Core areas:

- Session audit intake: every supplied session analysis must begin from the existing Obsidian audit checklist.
- Real-use feedback loop: audit findings become Flow specs/tasks in Plugin development, not only notes.
- Built-in safe git workflow: ACC can inspect status, classify paths, protect ACC state/secrets/env, checkpoint, verify, stage, commit, and gate push/PR.
- Canonical state updates: ACC workflow state must record active goal, progress, verification, commits, learned corrections, and next action after meaningful work.
- Learning evidence: auto-learning must either write durable Markdown/receipt evidence or not claim it happened.
- Compaction recovery: after compaction, ACC visibly re-anchors before more edits.

Likely implementation regions:

- `plugins/anyone-can-code/scripts/`
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md`
- `plugins/anyone-can-code/skills/execute/SKILL.md`
- `plugins/anyone-can-code/skills/verify/SKILL.md`
- `plugins/anyone-can-code/skills/learn/SKILL.md`
- `plugins/anyone-can-code/scripts/front_door.py`
- `plugins/anyone-can-code/scripts/canonical_state.py`
- `plugins/anyone-can-code/scripts/status_model.py`
- tests under `plugins/anyone-can-code/tests/`
- validation and docs under `plugins/anyone-can-code/`

## API Contracts
<!-- scope: technical -->

Candidate scripts or modules must expose deterministic interfaces suitable for skills and tests.

Potential contracts:

- `scripts/git_workflow.py status --project-root <path> --json`
- `scripts/git_workflow.py plan --project-root <path> --json`
- `scripts/git_workflow.py manage --project-root <path> [--commit] [--push] [--pr] --json`
- `scripts/session_audit_preflight.py --session <path> --project-root <path> --json`
- `scripts/memory_preflight.py` remains the recall path and should support post-learn readback.
- `scripts/canonical_state.py` or a new helper records git-workflow evidence into canonical ACC state.

Outputs must include:

- safe paths
- risky paths
- blocked paths
- checkpoint path when created
- verification result
- commit SHA when created
- push/PR decision and explicit reason
- receipt path
- state update path
- unproven/unknown items

## Edge Cases & Constraints
<!-- scope: technical -->

- Do not use ACC runtime, hooks, MCP, or skills inside Plugin development while building this.
- Do not push, PR, tag, publish, release, or touch remotes unless explicitly commanded.
- Preserve dirty/untracked work.
- Never commit `.codex/anyone-can-code` project state by default.
- Block env files, secret-like files, credentials, generated caches, and foreign plugin state unless explicitly approved.
- Remote push and PR creation are gated, never automatic from broad "handle everything" wording.
- Hook absence or hook failure must not break core git workflow or learning.
- Auto-learning must not silently scrape sessions.
- Session import remains explicit selected-path only.
- Compaction and abort recovery must reread state/files before more edits.
- Existing Zenfit repo-local git manager is evidence/prototype only; ACC core is the product target.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** A supplied session audit request first consults the Obsidian audit checklist notes before summarizing.
- **R2:** Real-use findings can be recorded as Flow specs/tasks in Plugin development with Obsidian links.
- **R3:** ACC source includes a built-in safe git workflow capability or clearly scoped module that can classify safe/risky/blocked paths.
- **R4:** ACC can create a rollback/checkpoint receipt before staging or committing user project changes.
- **R5:** ACC can run configured verification before commit and records exactly what passed or failed.
- **R6:** ACC blocks `.codex/anyone-can-code`, env files, secret-like paths, generated caches, and remote actions by default.
- **R7:** ACC records meaningful git workflow progress into canonical state or status-visible receipts so `$status` cannot appear blank after real work.
- **R8:** Explicit `$learn` performs a write and readback proof, or reports why readback is not proven.
- **R9:** Auto-learning claims are backed by durable Markdown or receipt evidence; otherwise wording says no auto-learn happened.
- **R10:** After compaction, ACC visibly re-anchors before editing: project rules, current task, git state, and exact target files.
- **R11:** Installed runtime QA proves the built-in capability in a normal project without using Plugin development as helper runtime.
- **R12:** Docs explain that ACC is the workflow owner and deterministic helper modules are implementation details, not separate managers the user must understand.

## Boundaries
<!-- scope: business -->

Out of scope for first implementation:

- Building a UI memory viewer.
- Running Session Analyzer or modifying old analyzer dumps.
- Importing arbitrary sessions automatically.
- Remote push/PR execution without explicit command.
- Replacing all project-specific build/test scripts.
- Guaranteeing every possible app stack; first version can support common git workflows with configurable verification.

## Decision Context
<!-- scope: both -->

The Zenfit trial made the problem concrete. ACC had enough guidance to tell the user not to blindly commit everything, but it lacked a reusable core mechanism to perform safe git workflow automatically. The agent solved it locally by building `scripts/git_manager/` inside Zenfit. That was useful as evidence, but not the desired product shape.

ACC should absorb the pattern into plugin core: the user should experience ACC handling routine project mechanics, not ACC building a new mini-manager in every project. Local project helpers may still exist as optional adapters, but the product capability belongs in ACC.
