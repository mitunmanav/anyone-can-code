---
satisfies: [R7, R10, R11, R13, R15, R20, R21]
---

## Description
Add exact observability states and verification wording so ACC never collapses in scope, designed, approved, implemented, verified, blocked, and deferred. Status output must stay human-readable for builders and developers.

**Size:** M
**Files:**
- `plugins/anyone-can-code/skills/status/SKILL.md`
- `plugins/anyone-can-code/skills/verify/SKILL.md`
- `plugins/anyone-can-code/skills/execute/SKILL.md`
- `plugins/anyone-can-code/scripts/doctor.py`
- `plugins/anyone-can-code/scripts/product_intake.py`
- `plugins/anyone-can-code/VALIDATION.md`
- `.codex/anyone-can-code/state/workflow.json` (generated state)

## Approach
- Define the allowed state vocabulary once and reuse it in status/verify/execute guidance.
- Status line should be compact: `Status: implemented, tests verified, deploy blocked`.
- Verification records must include evidence and uncertainty.
- Keep code and output explainable; avoid hidden magic.

## Investigation targets
**Required** (read before coding):
- `plugins/anyone-can-code/skills/verify/SKILL.md:10` - verification goals.
- `plugins/anyone-can-code/skills/verify/SKILL.md:33` - built is not verified rule.
- `plugins/anyone-can-code/skills/status/SKILL.md` - current status inputs.
- `plugins/anyone-can-code/skills/execute/SKILL.md` - task execution state updates.
- `plugins/anyone-can-code/scripts/setup.py:132` - workflow state defaults.
<!-- Updated by plan-sync: fn-1-define-project-direction.1 moved workflow defaults into `workflow_defaults` during persona setup repair -->
- `plugins/anyone-can-code/scripts/product_intake.py` - task `.2` introduced `ALLOWED_STATES` and checklist item states; decide whether to reuse or move shared state vocabulary.
<!-- Updated by plan-sync: fn-1-define-project-direction.2 added checklist item states and product intake doctor smoke. -->

**Optional** (reference as needed):
- `plugins/anyone-can-code/README.md` - evidence-first rule.

## Key context
The state vocabulary is closed: in scope, designed, approved, implemented, verified, blocked, deferred. New synonyms should not leak into status output.

Task `.2` currently keeps the same state vocabulary in `product_intake.ALLOWED_STATES`; `.4` should make the reusable source explicit for status/verify/execute.

## Acceptance
- [ ] Status output uses only allowed states and reports failures, silent failures, and unverified work.
- [ ] Verify guidance records checked evidence, pass/fail, and remaining uncertainty.
- [ ] Execute guidance updates workflow state without claiming unverified work is complete.
- [ ] A developer can understand current route, state, and next step from local files within 10 minutes.
- [ ] Windows doctor/validation checks cover status vocabulary or generated state shape.

## Done summary
Added one closed workflow state vocabulary, evidence-first status rendering, verification records, generated state repair, Doctor checks, and status/verify/execute guidance. Built work stays implemented until proof marks it verified. Failures, silent failures, unverified work, uncertainty, route, and next step remain visible.
## Evidence
- Commits: 571c07d
- Tests: python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py: 29 OK in development and testing, python plugins\anyone-can-code\scripts\doctor.py --json: 24 PASS, 0 WARN, 0 FAIL after normal setup repair in testing, python -m py_compile status/setup/doctor/state scripts: PASS, python .flow\bin\flowctl.py validate --all --json: 3 specs, 12 tasks, 0 errors, 0 warnings, promotion guard 81eac35..571c07d plugin-product: PASS, 11 changed files, testing candidate 77badae: clean and verified
- PRs: