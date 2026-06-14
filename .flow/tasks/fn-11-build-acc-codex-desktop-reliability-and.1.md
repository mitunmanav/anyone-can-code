# fn-11-build-acc-codex-desktop-reliability-and.1 Freeze ACC operating contracts and platform limits

## Description
Define ACC operating contract before implementation. Contract must cover
workflow ownership, bounded specialists, canonical working state, failure
recovery, user-visible output, dangerous-action approval, automatic safe work,
questions during work, scope changes, organized history, efficiency, and
proven Codex Desktop platform limits.

Requirement changes must preserve old plans and proof as linked history while
moving active work to new approved state. Every affected plan, task, status,
resume, guidance, evidence, and brain file must agree before update is treated
as complete. ACC must not continue superseded work by mistake.
## Acceptance
- [ ] Coordinator, state, evidence, fallback, and user-output contracts are explicit.
- [ ] Official Codex limits are recorded without impossible promises.
- [ ] Caveman default and efficiency rules are included.
- [ ] ACC blocks workflow takeover unless user explicitly hands off ownership.
- [ ] Specialists receive bounded jobs and return results to ACC.
- [ ] Canonical state stores goal, active task, decisions, boundaries, progress, proof, failures, warnings, and next action.
- [ ] Normal failure retry is bounded; risky retry is stricter; circuit breaker and fallback are defined.
- [ ] Default user view is simple while full technical proof remains available.
- [ ] Dangerous actions require exact immediate approval.
- [ ] User questions pause work, receive simple truthful answers, and preserve resume position.
- [ ] Safe reversible work proceeds automatically.
- [ ] Scope changes preserve old history, update every affected file, invalidate affected proof, activate new work, and prevent stale-plan continuation.
## Done summary
Defined and froze the ACC operating contract with user-approved rules for
workflow ownership, bounded specialists, canonical state, failure recovery,
communication, approvals, automatic safe work, scope changes, verification,
memory conflict prevention, missing information, privacy, background work,
completion evidence, and proven Codex Desktop limits.

Created `ACC-OPERATING-CONTRACT.md`. Updated Flow and complete Obsidian brain.
No plugin behavior code or GitHub action occurred.
## Evidence
- Commits:
- Tests: flowctl validate --spec fn-11-build-acc-codex-desktop-reliability-and: 0 errors, 0 warnings, Obsidian affected-note link check
- PRs: