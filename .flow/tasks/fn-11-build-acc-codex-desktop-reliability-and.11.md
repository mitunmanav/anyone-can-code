# fn-11-build-acc-codex-desktop-reliability-and.11 Run installed Codex Desktop real-user QA

## Description
TBD

## Acceptance
- [x] Test installed ACC in Codex Desktop, not source files only.
- [x] Cover natural setup, plan, build, correction, learning, compaction, new chat, resume, verification, hook failure, and plugin conflict.
- [x] Record user interventions, false-done claims, next-step questions, and recovery success.
- [x] No test converts unavailable behavior into a false pass.


## Done summary
Installed Codex Desktop runtime QA passed after explicit user-approved installed cache refresh. Old installed caches were backed up, safety receipt written, both installed ACC cache folders refreshed from current source, and installed-runtime QA receipt passed all required scenarios without false pass.
## Evidence
- Commits:
- Tests: python plugins/anyone-can-code/scripts/installed_runtime_qa.py --write-receipt --json (pass; receipt installed-qa-20260614T132953Z-f95d411a), python -m unittest discover plugins/anyone-can-code/tests (90 OK), python plugins/anyone-can-code/scripts/doctor.py --json (33 PASS, 0 WARN, 0 FAIL)
- PRs:
