Description

Reproduce the ACC routed-request path where the user gives a meaningful build/design request after `anyone-can-code:help`, the progress UI advances, but the visible assistant response stays empty or silent.

Known user evidence from 2026-06-14:
- Normal test project: `C:\Users\Mitun Manav G Y\Desktop\website portfolios`.
- User had just run ACC update and restarted Codex.
- ACC help response appeared normally.
- User then requested a polished existing demo website using ACC, brainstorming, product design, and UI skills.
- Codex showed progress for about one minute, but no useful visible assistant reply appeared.

Fix must make ACC always answer visibly after routed user input, even if the answer is a question, a handoff notice, a plan, or a safe failure message.

Acceptance

- [ ] A regression test or reproducible harness covers the silent routed-response path.
- [ ] ACC always emits a user-visible response after meaningful routed input.
- [ ] The response explains next step plainly when ACC needs clarification or a design route.
- [ ] Normal project update flow still passes Doctor with no FAIL.
- [ ] Plugin development keeps ACC disabled as helper during the repair.
- [ ] Obsidian and Flow are updated with evidence after verification.

## Description
Reproduced exact 2026-06-14 request and confirmed two source-side causes:
- Existing website improvement was classified as idea + website.
- Front-door routes had no deterministic visible-response completion contract.

Implemented locally:
- Existing-site improvement routes to polish-review + website.
- Every route returns response_contract requiring visible summary and next action.
- Empty or unusable specialist output requires same-turn ACC fallback text.
- Orchestrator and bridge forbid progress-only completion.
- Codex Desktop rendering remains platform-owned and cannot be claimed fixed from source tests.

Verification completed:
- Focused RED then GREEN tests.
- 94 full plugin tests pass.
- Python compile passes.
- Doctor 33 PASS, 0 WARN, 0 FAIL.
- Flow validates with 0 errors and 0 warnings.

Remaining gate:
- Run installed normal-project new-chat QA and confirm returned text is visibly rendered in Codex Desktop.
## Acceptance
- [x] Regression test covers exact existing-website request and old wrong route.
- [x] Existing-site improvement routes to polish/review, not new-idea intake.
- [x] Every route carries visible summary and next-action requirements.
- [x] Empty specialist output requires same-turn ACC fallback text.
- [x] Plugin tests, compile, Doctor, and Flow validation pass.
- [x] Plugin development kept ACC disabled as helper.
- [x] Repo docs, Flow, and Obsidian updated with evidence.
- [ ] Installed normal-project Codex Desktop new-chat QA proves returned text is visibly rendered.
## Done summary
Source repair completed and verified: existing-site request routes to polish/review, every route carries visible response contract, empty specialist output requires same-turn ACC fallback. Installed UI rendering proof split to fn-13.2.
## Evidence
- Commits:
- Tests: Focused route/contract tests passed before split, Full plugin tests: 94 passed before later reliability work, Compile passed, Doctor 33 PASS / 0 WARN / 0 FAIL, Flow validate passed
- PRs: