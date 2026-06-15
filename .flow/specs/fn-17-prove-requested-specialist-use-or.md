# fn-17-prove-requested-specialist-use-or Prove requested specialist use or fallback

## Goal & Context
<!-- scope: business -->

Audit evidence shows user explicitly requested ACC with brainstorming, Product Design, Build Web Apps / UI skills, but Product Design and Build Web Apps were not actually loaded and fallback was not plainly reported. ACC must make requested specialist handling visible and evidence-based: if user names a specialist/plugin/capability, ACC either proves which installed provider was selected or says why it fell back to ACC.

## Architecture & Data Models
<!-- scope: technical -->

Extend front-door/bridge routing in `plugins/anyone-can-code/scripts/front_door.py` without using ACC runtime hooks or skills in this development project.

Add a request-level specialist resolution summary separate from the single best plugin route:

- extract explicit specialist intents from request text;
- match each intent against installed plugin/capability metadata already scanned by the bridge;
- record `requested`, `matched`, `plugin`, `reason`, and fallback owner;
- keep ACC as workflow owner unless user explicitly hands off;
- do not treat generic weak overlap as proof of use.

Skill/docs text must require visible reporting of loaded specialists and fallbacks.

## API Contracts
<!-- scope: technical -->

`route_request(...)` returns existing fields unchanged and may add:

```json
"requested_specialists": [
  {
    "requested": "product design",
    "matched": true,
    "plugin": "product-design",
    "reason": "explicit-request-installed-match",
    "fallback": {"owner": "acc", "route": "local-acc"}
  }
]
```

If a requested specialist is not confidently available, `matched` is false and `reason` explains `requested-specialist-unavailable` or equivalent.

## Edge Cases & Constraints
<!-- scope: technical -->

- Do not use ACC plugin runtime, ACC hooks, ACC MCP, or ACC skills in this project.
- Do not route to ACC itself as a specialist.
- Do not silently omit requested specialists.
- Multiple requested specialists can be recorded even when only one best plugin route is selected.
- Missing or unhealthy specialists must not block normal ACC work; they must be reported as fallback.
- Specialist mention remains advisory and must not override fn-16 ownership containment.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** A request naming Product Design and Build Web Apps/UI returns a `requested_specialists` list with each requested specialist accounted for.
- **R2:** An installed matching specialist is marked matched with exact provider and source-based reason.
- **R3:** An unavailable or unhealthy requested specialist is marked unmatched with fallback to ACC and a plain reason.
- **R4:** ACC never claims specialist use unless installed metadata/probe supports it.
- **R5:** Existing single best plugin routing and ACC fallback behavior continue to pass current tests.
- **R6:** Bridge/orchestrator docs require visible reporting of which requested specialists were used and which fell back.
- **R7:** Verification includes focused regression tests, full plugin tests, compile, Doctor, and Flow validation.

## Boundaries
<!-- scope: business -->

- No installed Codex Desktop QA in this task unless separately requested.
- No hook observability repair; fn-14 owns that.
- No remote action, commit, push, PR, tag, release, or publish.
- No redesign of the whole capability registry.

## Decision Context
<!-- scope: both -->

Session exports prove the user-visible failure: requested specialists were not used, and ACC did not plainly report fallback. This is ACC bridge/product behavior, not a Codex Desktop platform-mechanics change. Existing manifest scanning already supplies enough local evidence for installed-provider proof, so this task should stay narrow: account for explicit requests, preserve ACC ownership, and add visible fallback reporting.
