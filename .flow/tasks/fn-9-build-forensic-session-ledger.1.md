# fn-9-build-forensic-session-ledger.1 Design forensic ledger data model and output map

## Description
﻿Define the v3 analyzer data model and exact output map before implementation.

Must cover:
- simple Obsidian reading layer
- raw forensic proof layer
- source/event/message/task/tool/token/hidden-reasoning schemas
- exact/derived/estimated/unknown/impossible labels
- cleanup gate design
- no ACC runtime or GitHub coupling
## Acceptance
﻿- [ ] Data model documented in Flow/Obsidian before implementation.
- [ ] Output map names every Markdown page and raw-data artifact.
- [ ] Hidden reasoning is metadata-only; decrypted text is impossible unless plaintext/key exists.
- [ ] Cleanup gate is explicit and cannot run during normal analysis.
## Done summary
Created Forensic Session Ledger data model and output map in Obsidian. It defines simple Markdown pages, raw forensic ledgers, SQLite tables, category model, exact/derived/estimated/unknown labels, Hidden Reasoning Metadata Analyzer shape, and old-run cleanup gate.
## Evidence
- Commits:
- Tests: flowctl validate --spec fn-9-build-forensic-session-ledger --json passed
- PRs: