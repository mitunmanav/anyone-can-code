# fn-18-prevent-unsupported-success-claims Prevent unsupported success claims

## Goal & Context
<!-- scope: business -->

Manual usage audit found ACC claimed or implied product success beyond evidence. Build, dependency audit, source scan, and HTTP 200 were checked, but interactive controls, visual quality, and user acceptance were not. ACC must label exact evidence level and avoid saying interactive/user-facing work "works", "proper", "perfect", "done", or "fully verified" unless the needed proof exists.

## Architecture & Data Models
<!-- scope: technical -->

Extend `plugins/anyone-can-code/scripts/status_model.py` with a small verification-claim helper. Keep the existing closed status vocabulary. Add evidence-level handling for verification records and user-facing claim text.

Evidence levels:

- `implemented`
- `source_inspected`
- `automated_tests`
- `build_passed`
- `dependency_audit`
- `http_smoke`
- `interaction_tested`
- `visual_qa`
- `user_accepted`

Interactive "works" claims require `interaction_tested`. Visual quality claims require `visual_qa`. "Perfect", "proper", "accepted", or equivalent user-acceptance claims require `user_accepted`. Missing levels must be reported as uncertainty, not hidden.

Update verification-facing skill/docs text so ACC says exact proof, e.g. `Build passed and HTTP smoke passed. Interactions and visual quality unverified.`

## API Contracts
<!-- scope: technical -->

Add helper functions to `status_model.py`:

- `normalize_evidence_levels(levels)` validates evidence level names.
- `assess_success_claim(claim, evidence_levels)` returns claim, supported bool, required levels, missing levels, and safe wording.
- `build_verification_record(...)` may include optional `evidence_levels`; when provided, result includes `evidence_levels` and `claim_assessments` if claims are supplied.

Existing callers remain compatible.

## Edge Cases & Constraints
<!-- scope: technical -->

- Do not use ACC runtime/hooks/MCP/skills in Plugin development.
- Do not change verified state vocabulary.
- Do not make ACC test forever; report remaining uncertainty honestly.
- Do not block source-only plugin repairs from being called source-verified when scope is source behavior.
- Installed Codex Desktop QA remains separate from source verification.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** `works` or equivalent interactive claim is unsupported without `interaction_tested`.
- **R2:** Visual quality claim is unsupported without `visual_qa`.
- **R3:** `perfect`, `proper`, `accepted`, or equivalent product-quality/user-acceptance claim is unsupported without `user_accepted`.
- **R4:** Safe wording lists what passed and what remains unverified.
- **R5:** Existing verification records without evidence levels remain backward compatible.
- **R6:** Verify/status/orchestrator docs require exact evidence-level wording.
- **R7:** Verification includes focused tests, full plugin tests, compile, Doctor, and Flow validation.

## Boundaries
<!-- scope: business -->

- No installed real-app QA in this task unless separately requested.
- No browser/server launch.
- No remote action, commit, push, PR, tag, release, or publish.
- No hook work; fn-14 owns hook observability.

## Decision Context
<!-- scope: both -->

This is ACC product truthfulness logic, not a Codex Desktop platform-mechanics change. The failure is fully described by audit evidence and project requirements R20/R45. Existing docs already require separating implementation, automated checks, real interaction verification, and user acceptance; this task turns that rule into a reusable helper and regression tests.