# fn-9-build-forensic-session-ledger.7 Verify current inbox and gate old-run cleanup

## Description
﻿Run full verification on current inbox and gate old-run cleanup.

After implementation and tests pass, run analyzer on current fixed inbox including folder `13`. Verify output is readable and complete. Do not delete old dump records until user reviews clean output and explicitly approves exact cleanup target/policy.
## Acceptance
﻿- [ ] Py compile passes for analyzer modules.
- [ ] Unit tests pass.
- [ ] Full current inbox run succeeds with zero parse failures for current valid inputs.
- [ ] `00_START_HERE.md` clearly points user to review queue, usage, hidden reasoning metadata, compaction, caveman, and sorted history.
- [ ] Old dump cleanup remains blocked unless user gives explicit post-verification approval.
## Done summary
Final verification passed. Compile passed, 21 unit tests passed, and current inbox run succeeded with 15 sources, 13,321 parsed records, 0 parse failures, 2 duplicate MD fallbacks skipped. Latest output has clean entry links, review queue, usage, hidden reasoning metadata, compaction, caveman, and raw proof ledgers. Old dump cleanup remains blocked pending user review and explicit cleanup approval.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py session_classification.py session_usage.py session_hidden_reasoning.py session_continuity.py, python -m unittest discover -s tests -v (21 OK), powershell -ExecutionPolicy Bypass -File .\run.ps1 -Label forensic-ledger-final-check-v2
- PRs: