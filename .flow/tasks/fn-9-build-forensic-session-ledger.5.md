# fn-9-build-forensic-session-ledger.5 Build hidden reasoning metadata analyzer

## Description
﻿Build Hidden Reasoning Metadata Analyzer.

Track encrypted reasoning metadata, not decrypted hidden text. Correlate encrypted blob hash/size/source/line/turn with nearby prompts, token snapshots, rate-limit snapshots, tools, failures, compactions, and outcomes.
## Acceptance
﻿- [ ] `HIDDEN_REASONING_METADATA.md` exists.
- [ ] `raw-data/hidden-reasoning-metadata.jsonl` exists.
- [ ] SQLite contains hidden reasoning metadata table or equivalent query support.
- [ ] Output never claims decrypted hidden reasoning text.
- [ ] Tests cover encrypted blob hash/size/context extraction.
## Done summary
Built Hidden Reasoning Metadata Analyzer. Added 05_HIDDEN_REASONING_METADATA.md, raw-data/hidden-reasoning-metadata.jsonl, and SQLite hidden_reasoning_metadata table. It links encrypted blob hash/size/source/turn to nearby prompts, token/rate-limit snapshots, following tools, and outcomes, without decrypting or claiming hidden text.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py session_classification.py session_usage.py session_hidden_reasoning.py, python -m unittest discover -s tests -v (20 OK)
- PRs: