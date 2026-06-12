---
satisfies: [R1, R6, R12, R16, R21, R24, R25]
---

## Description
Wire the orchestrator so ACC starts from one front door, detects the request shape, routes to intake/plan/execute/verify/learn/update as needed, and uses the bridge to avoid rebuilding work covered by installed plugins.

**Size:** M
**Files:**
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md`
- `plugins/anyone-can-code/skills/bridge/SKILL.md`
- `plugins/anyone-can-code/skills/onboard/SKILL.md`
- `plugins/anyone-can-code/skills/help/SKILL.md`
- `plugins/anyone-can-code/scripts/product_intake.py`
- `plugins/anyone-can-code/skills/*/agents/openai.yaml`
- `plugins/anyone-can-code/README.md`

## Approach
- Keep `$orchestrator` as the single front door.
- Route based on entry mode and confidence.
- Bridge should scan installed plugin manifests as advisory signal only, and return control to ACC when routed workflow goes null or cannot continue.
- If a plugin/skill is missing or uncertain, fall back to ACC local workflow.
- Dev-system concepts must stay out of shipped UX.

## Investigation targets
**Required** (read before coding):
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md:17` - current entry modes.
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md:36` - mode banner contract.
- `plugins/anyone-can-code/skills/bridge/SKILL.md:12` - bridge scan behavior.
- `plugins/anyone-can-code/scripts/product_intake.py` - deterministic intake/checklist/plan-line contract from task `.2`.
- `plugins/anyone-can-code/.codex-plugin/plugin.json:33` - default prompts.
<!-- Updated by plan-sync: fn-1-define-project-direction.2 added `scripts/product_intake.py` as the request-to-plan helper and updated orchestrator guidance. -->

**Optional** (reference as needed):
- `plugins/anyone-can-code/skills/help/SKILL.md` - user help surface.
- `plugins/anyone-can-code/README.md` - user-facing workflow.

## Key context
Bridge detection is approximate. The UX should say what was detected and routed, but not claim unavailable tools exist.

The vague-idea route should now reuse `product_intake.py` behavior instead of inventing a second intake/classifier path.

## Acceptance
- [ ] Orchestrator accepts vague idea, existing repo, feature, bug, polish, ship, and verify starting points.
- [ ] Orchestrator shows route in a compact banner before continuing.
- [ ] Bridge checks installed plugin manifests before duplicating capability.
- [ ] Missing/null plugin coverage falls back to local ACC flow.
- [ ] User-facing route never exposes candidate/stable workflow, audit ledger, proof journal, or phase-gate internals.
- [ ] Route guidance covers local docs first, web on doubt/stale docs, and efficient subagent reading when useful.
- [ ] Mid-work requirement changes update plan/state and resume from correct position.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
