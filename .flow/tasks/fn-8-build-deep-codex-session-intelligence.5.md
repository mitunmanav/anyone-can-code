---
satisfies: [R1, R4, R7, R8, R9, R10, R11, R14, R16, R17]
---

## Description
Build structural privacy pipeline and compact report suite that exposes maximum useful evidence with minimum future chat rereading and no automatic ACC promotion.

**Size:** M
**Files:** `../session-analyzer/session_privacy.py`, `../session-analyzer/session_reports.py`, `../session-analyzer/analysis-prompt.md`, `../session-analyzer/README.md`, `../session-analyzer/tests/test_session_reports.py`

## Approach
- Sanitize before serialization or excerpt generation.
- Report redaction categories/counts without exposing originals.
- Generate aggregate-first machine files and readable Markdown with fact/inference/recommendation/unknown separation.
- Keep full sanitized evidence separate from compact normalized outputs.
- Produce approval-gated, desensitized ACC candidate entries.

## Investigation targets
**Required:**
- `../session-analyzer/session_analyzer.py:20-47` - current sensitive-key and regex coverage.
- `../session-analyzer/analysis-prompt.md` - current interpretation contract.
- `../session-analyzer/README.md` - operator documentation.
- `offical-codex-docs/core/agent-approvals-security.md` - prompt/log privacy guidance.
- `Projects/Anyone Can Code/27 Session Analyzer Architecture.md` - dump/promotion boundary.

**Optional:**
- `offical-codex-docs/learn/best-practices.md` - compact context and reusable workflow guidance.

## Acceptance
- [ ] Output includes synchronized `forensic-index.json` and `intelligence-summary.json` with shared evidence/metric references.
- [ ] Maximum-detail output stays private; compact output is sufficient for routine future analysis.
- [ ] Ranking formulas and confidence meanings are documented and visible.
- [ ] Secrets, credentials, sensitive keys, emails, paths, environment values, and risky excerpts are redacted before any output write.
- [ ] Output suite matches spec contract and routine facts can be read without loading full sanitized evidence.
- [ ] Deep report states exact evidence, formulas, confidence, limitations, and actionable efficiency findings.
- [ ] Candidate brain entries are desensitized and clearly blocked on explicit user approval.
- [ ] README explains manual operation, privacy, observable-vs-hidden limits, and output meanings.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
