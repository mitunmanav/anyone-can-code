Built deterministic product intake and adaptive checklist flow.

- Added `scripts/product_intake.py` with product classification, five-question intake, checklist generation, plan-line rendering, and smoke check.
- Added tests for vague request intake, skipped known answers, required product types, checklist decisions, plan-line output, and doctor smoke reporting.
- Updated clarify, plan, orchestrator, doctor, and validation docs to anchor the request-to-plan behavior.
- Codex implementation review blocked on Windows by `PermissionError: [WinError 5] Access is denied` when launching Codex CLI.
