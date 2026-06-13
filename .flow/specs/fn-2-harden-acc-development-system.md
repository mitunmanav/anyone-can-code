# fn-2-harden-acc-development-system Harden ACC development system

## Goal & Context
<!-- scope: business -->

ACC plugin development currently feels hard to trust because state is spread across repo files, Flow specs/tasks, Obsidian project brain, runtime cache, and three local worktrees. The goal is not to add ACC product features or change plugin runtime behavior. The goal is to make the development system reliable enough that work on the actual plugin can resume with confidence.

Flow-Next becomes the technical control plane for this reliability work. Obsidian remains the full project brain and history. Repo docs describe workflow rules. The development system must make missed updates visible quickly: if a change affects docs, Flow, Obsidian, runtime cache, or worktree sync, there must be a checklist or verification path that catches the miss before work is called done.

## Architecture & Data Models
<!-- scope: technical -->

Use Flow-Next as the task/state backbone. Add a dedicated Flow spec for development reliability and use its tasks as the checklist for future hardening work.

The system has four layers:

1. Flow task graph: this spec owns reliability tasks and acceptance criteria.
2. Workflow docs: `AGENTS.md`, `DEVELOPMENT-WORKFLOW.md`, and Obsidian notes state what must be updated for each change type.
3. Verification receipts: each reliability task records exact command evidence before completion.
4. Manual gate before plugin feature work: agents must re-anchor on Flow and Obsidian, then run the current verification checklist before claiming success.

No plugin source files under `plugins/anyone-can-code/**` are changed by this spec unless the user later explicitly allows it. Runtime cache may be checked, but not treated as source of truth.

## API Contracts
<!-- scope: technical -->

This spec defines process contracts, not application APIs.

Change-impact contract:

- Plugin source or hook behavior change requires tests, Doctor, runtime cache check, Flow evidence, repo docs if workflow/setup changed, and Obsidian evidence.
- Flow spec/task change requires `flowctl validate --all`, Obsidian status/evidence update, and task map review.
- Obsidian decision/status change requires wiki-link check and current-status consistency check.
- Worktree merge or sync change requires root/dev/test status, commit hashes, tests or validation evidence for affected worktrees, and GitHub no-push proof.
- Runtime cache change requires source/cache hash or behavior check and explicit note that local source remains authoritative.

Completion contract:

- A task is not done until Flow evidence, Obsidian evidence, and verification commands agree.
- Online GitHub actions remain forbidden unless user explicitly commands them.

## Edge Cases & Constraints
<!-- scope: technical -->

- User explicitly said this is about the development system around the plugin, not plugin product behavior.
- Do not edit plugin files for this reliability setup unless user explicitly changes scope.
- Flow owns technical task state only; Obsidian owns full history, decisions, and evidence.
- Development happens in dev worktree; testing happens in test worktree; root main remains approved clean code.
- The system must improve speed, not add heavy ceremony.
- Checks may start manual and Flow-driven; automation can be added later if it proves useful.
- Existing remote PR/branch state must not be changed without explicit command.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** A Flow spec exists for ACC development reliability and is separate from ACC product feature work.
- **R2:** The spec states that plugin source files under `plugins/anyone-can-code/**` are out of scope for this setup unless explicitly approved.
- **R3:** A change-impact matrix exists in repo docs or Obsidian and maps change types to required updates and checks.
- **R4:** A completion checklist exists for future ACC work and includes Flow validation, tests/Doctor as applicable, Obsidian update, worktree status, runtime cache check when relevant, and GitHub no-push proof.
- **R5:** Flow tasks represent the reliability work in small steps that can be completed before returning to product task `.3`.
- **R6:** Running `flowctl validate --all` passes after the reliability spec/tasks are created.
- **R7:** Obsidian records what changed, why this is development-system work, and what remains before product work resumes.

## Boundaries
<!-- scope: business -->

In scope:

- Flow spec/tasks for the development reliability system.
- Repo workflow documentation.
- Obsidian project brain updates.
- Manual verification checklist and evidence rules.
- Runtime cache verification rules when relevant.

Out of scope:

- Changing ACC plugin source files.
- Implementing new ACC product behavior.
- Pushing, merging, PR creation, tagging, publishing, or release.
- Replacing Obsidian or Flow with a new tracker.
- Building a large automation framework before the manual reliability loop is trusted.

## Decision Context
<!-- scope: both -->

The selected approach is a Flow-first development reliability system around the plugin, not inside the plugin. This matches the user's correction: use plugin capabilities and Flow-Next to maximize reliability, but do not modify plugin files just to create process confidence.

Alternative rejected: immediately adding verifier code inside the plugin. That would blur product behavior with development workflow and violate the current constraint.

Alternative rejected: relying only on chat memory and broad instructions. That already produced the trust gap: updates can be missed when state is distributed.

This spec makes Flow the small technical spine for hardening work while preserving Obsidian as the full project brain.
