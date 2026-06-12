---
satisfies: [R8, R9, R10, R12, R16, R17, R18, R19, R25]
---

## Description
Add guardrails for learning, Git/GitHub handling, and rollback so ACC can describe and prepare safe automation without pretending full shipping automation exists before intake works.

**Size:** M
**Files:**
- `plugins/anyone-can-code/skills/learn/SKILL.md`
- `plugins/anyone-can-code/skills/execute/SKILL.md`
- `plugins/anyone-can-code/skills/verify/SKILL.md`
- `plugins/anyone-can-code/mcp/server.py`
- `plugins/anyone-can-code/scripts/doctor.py`
- `plugins/anyone-can-code/VALIDATION.md`
- `plugins/anyone-can-code/README.md`

## Approach
- Memory remains MCP-first and advisory.
- Retrieval stays capped at top 3-5 lessons.
- Git/GitHub/PR/rollback should be represented as explicit states and guardrails, not hidden automation.
- Full automation can be deferred, but unsafe claims must be blocked; secrets, paid service choices, account logins, destructive actions, and product decisions are user-only asks.
- Dev-system build controls must not become shipped UX.

## Investigation targets
**Required** (read before coding):
- `plugins/anyone-can-code/mcp/server.py:20` - memory scopes.
- `plugins/anyone-can-code/mcp/server.py:30` - default retrieval limit.
- `plugins/anyone-can-code/mcp/server.py:173` - retrieve context behavior.
- `plugins/anyone-can-code/mcp/server.py:221` - store feedback behavior.
- `plugins/anyone-can-code/skills/learn/SKILL.md` - learning rules.
- `plugins/anyone-can-code/README.md` - memory and upgrade model.

**Optional** (reference as needed):
- `plugins/anyone-can-code/hooks/hooks.json` - current hook events.
- `plugins/anyone-can-code/VALIDATION.md` - safety checklist.

## Key context
R8 is allowed to be guardrail/scaffold in this first spec. The boundary says full GitHub PR automation and complete rollback implementation are out of scope until intake works.

## Acceptance
- [ ] Learning guidance retrieves only top 3-5 relevant lessons.
- [ ] Memory text states that memory is advisory and never truth by itself.
- [ ] Git/GitHub/rollback guidance records whether actions are in scope, designed, approved, implemented, verified, blocked, or deferred.
- [ ] No user-facing skill suggests full PR/rollback automation is complete before implementation exists.
- [ ] Validation docs include checks preventing dev-system concepts from leaking into shipped UX.
- [ ] Model/task fit learning is captured from local session evidence when available.
- [ ] Missing requirements found mid-work are surfaced instead of ignored.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
