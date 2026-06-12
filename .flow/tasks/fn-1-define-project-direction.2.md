---
satisfies: [R1, R2, R3, R4, R14, R15, R23]
---

## Description
Build the first useful product flow: user gives a vague product request, ACC asks up to five blocking intake questions, classifies product type, generates an adaptive engineering checklist, and renders one concise plan line.

**Size:** M
**Files:**
- `plugins/anyone-can-code/skills/clarify/SKILL.md`
- `plugins/anyone-can-code/skills/plan/SKILL.md`
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md`
- `plugins/anyone-can-code/scripts/doctor.py`
- `plugins/anyone-can-code/VALIDATION.md`
- New or existing helper module under `plugins/anyone-can-code/scripts/`

## Approach
- Keep intake deterministic and small before deeper automation.
- Five blocking questions are fixed unless user already supplied an answer.
- Checklist adapts by product type instead of printing every possible area.
- Plan line is builder-readable and hides low-level tooling.
- Avoid implementation-specific UX promises until the flow is verified.

## Investigation targets
**Required** (read before coding):
- `plugins/anyone-can-code/skills/clarify/SKILL.md:6` - current intake rules.
- `plugins/anyone-can-code/skills/plan/SKILL.md:12` - current plan outputs.
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md:8` - front-door role.
- `.flow/specs/fn-1-define-project-direction.md` - R1-R4 details.

**Optional** (reference as needed):
- `plugins/anyone-can-code/skills/onboard/SKILL.md` - entry-mode language.
- `plugins/anyone-can-code/README.md` - core workflow summary.

## Key context
The user-facing proof point is: request `I want to build a website` leads to concise plan output such as `Plan: website + auth + deploy. Payments later.`

## Acceptance
- [ ] Intake asks no more than five blocking questions.
- [ ] Intake skips questions already answered by user context.
- [ ] Product classifier handles at least website, app, game, API, script, automation, plugin, data tool, dashboard, native app, existing repo, production repo, and unknown.
- [ ] Checklist marks each relevant engineering/UX area as include, defer, skip, or unknown.
- [ ] Output includes one concise plan line understandable by a non-technical builder.
- [ ] Validation docs include a smoke check for request-to-plan behavior.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
