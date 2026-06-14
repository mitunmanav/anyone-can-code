# fn-9-build-forensic-session-ledger.6 Build compaction and caveman reports

## Description
﻿Build compaction and caveman reports.

Detect context-compacted events, whether active anchor survived/reappeared, caveman instruction survival/drift, assistant/subagent/report verbosity, and visible-token-saving opportunities.
## Acceptance
﻿- [ ] Compaction report links each compaction to before/after task context.
- [ ] Re-anchor pass/fail or review-needed status exists for each compaction.
- [ ] Caveman report covers user-visible messages, final answers, status updates, subagent prompts/results where exported.
- [ ] Token-savings claims are exact/derived/estimated/unknown, never assumed.
- [ ] Tests cover compaction and caveman detection.
## Done summary
Built compaction/context-loss and caveman/token-saving reports. Added 06_COMPACTION_AND_CONTEXT_LOSS.md, 07_CAVEMAN_TOKEN_SAVINGS.md, compaction-analysis.jsonl, and caveman-analysis.jsonl. Real run found 12 compaction rows and 2,745 visible assistant/developer verbosity rows.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py session_classification.py session_usage.py session_hidden_reasoning.py session_continuity.py, python -m unittest discover -s tests -v (21 OK)
- PRs: