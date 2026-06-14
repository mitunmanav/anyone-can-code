# fn-9-build-forensic-session-ledger.4 Build usage cost and rate-limit reports

## Description
﻿Build usage-cost and rate-limit reports.

Reports must show per-session and per-task cost, per-message cost where evidence allows, rate-limit pressure timeline, compaction cost, repeated/failed action cost, and label each number exact/derived/estimated/unknown.
## Acceptance
﻿- [ ] Token snapshots are normalized into queryable raw data.
- [ ] Per-session and per-task usage tables exist.
- [ ] Per-message usage is shown only when evidence supports exact/derived/estimated labels.
- [ ] Rate-limit percent/reset/window data is shown when exported.
- [ ] Tests cover exact vs estimated vs unknown labeling.
## Done summary
Built usage-cost reports and ledgers. Added 04_USAGE_COSTS.md plus session-usage.jsonl, task-usage.jsonl, and message-usage.jsonl with exact/derived/estimated/unknown labels. Real run produced 15 session rows, 209 task rows, and 3,224 message usage rows.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py session_classification.py session_usage.py, python -m unittest discover -s tests -v (19 OK)
- PRs: