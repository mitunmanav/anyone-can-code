# fn-9-build-forensic-session-ledger.3 Build smart sorting and review index

## Description
﻿Replace folder-only bucket logic with smart sorting and a review index.

Date/collection folders like `13` are not semantic project categories. Classifier must use prompts, instructions, cwd/workspace, file paths, tools, branches, Flow/task names, Obsidian links, repo names, and plugin/runtime names.
## Acceptance
﻿- [ ] Each session gets suggested category, confidence, evidence, conflicting evidence, and review state.
- [ ] Low-confidence sessions go to Review Needed.
- [ ] User correction index is durable and reused by future runs.
- [ ] Folder bucket is only strong when user deliberately used official bucket folders.
- [ ] Tests cover date folder not deciding category.
## Done summary
Built smart sorting and review queue. Added classifier using prompt/message/path/tool evidence, classifications.jsonl, SQLite classifications table, and 02_SESSION_REVIEW_QUEUE.md. Real run classified 15 current sessions: 12 Plugin Development / ACC Source Work, 3 Website / Other Project Work; 7 review-needed due conflicts.
## Evidence
- Commits:
- Tests: python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py session_classification.py, python -m unittest discover -s tests -v (18 OK)
- PRs: