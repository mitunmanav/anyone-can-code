---
satisfies: [R8, R9, R10, R12, R17, R18, R19, R21, R25]
---

## Description
After the portable Markdown memory and setup spec is complete, add final learning, Git/GitHub, and rollback guardrails. Learning must use the new linked-Markdown memory folder, not legacy JSONL. Existing local session files are user-provided import sources and must enter through the same explicit Markdown migration path.

## Acceptance
- [x] Learning retrieves only top 3-5 relevant Markdown lessons.
- [x] Existing local session files can be imported only after explicit user selection, backup, deduplication, and receipt.
- [x] Imported session lessons are scoped as project, user, or shared and stay readable as Markdown.
- [x] Memory remains advisory and never truth by itself.
- [x] Git/GitHub/rollback actions use exact workflow states.
- [x] No remote action is claimed without evidence.
- [x] Risky work has a backup or Git rollback path before execution.
- [x] No user-facing skill suggests automation exists before implementation.
- [x] Missing requirements found mid-work are surfaced.
- [x] Dev-system concepts do not leak into shipped UX.

## Done summary
Closed original learning, Git/GitHub, and rollback guardrails after roadmap foundation and installed-runtime QA passed. Guardrails now use portable Markdown memory, canonical state, safety receipts, rollback/backup evidence, remote authority evidence, and no false remote claims.
## Evidence
- Commits:
- Tests: installed QA receipt installed-qa-20260614T132953Z-f95d411a passed, python -m unittest discover plugins/anyone-can-code/tests (90 OK), Doctor 33 PASS, 0 WARN, 0 FAIL, Flow validation passed, git diff --check passed
- PRs: