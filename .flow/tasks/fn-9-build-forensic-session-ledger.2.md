# fn-9-build-forensic-session-ledger.2 Build complete event and message ledgers

## Description
﻿Build complete event and message ledgers from JSONL/NDJSON/JSON-line source truth.

Must preserve every parsed/failed source line with evidence ID and raw-line SHA-256. Visible prompts/messages/instructions must be ledgered privately and surfaced as readable excerpts in Markdown.
## Acceptance
﻿- [ ] Every parsed or failed source line has source, line number, evidence ID, and SHA-256.
- [ ] User prompts, assistant visible messages, developer/system/project instruction layers, and replacement-history text are extracted when exported.
- [ ] Raw ledgers are machine-readable and linked from readable Markdown.
- [ ] Tests cover prompt/message extraction and source-line proof.
## Done summary
Built complete source/event/message/task raw ledgers. Added raw-data/sources.jsonl, events.jsonl, messages.jsonl, tasks.jsonl, raw-line SHA-256 in event records, message text hashes and sanitized text, and SQLite messages table. Real inbox run produced 15 sources, 13,321 events, 3,224 messages, and 209 tasks.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py, python -m unittest discover -s tests -v (17 OK)
- PRs: