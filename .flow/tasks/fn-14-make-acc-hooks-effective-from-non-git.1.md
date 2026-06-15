# fn-14-make-acc-hooks-effective-from-non-git.1 Repair nested project hook resolution and prove useful effects

## Description
TBD

## Acceptance
- Implement bounded nested ACC project discovery shared by all hook scripts.
- Block ambiguous nested candidates without selecting one silently.
- Start one correlated append-only receipt before project discovery for every
  ACC hook attempt.
- Record session/turn IDs, hook event, launcher start, script entry, cwd,
  resolver candidates, chosen project, returned context/output digest,
  state-write paths/results, skip/failure reason, exit status, duration, circuit
  state, and final effectiveness.
- Preserve unresolved-project evidence in bounded workspace fallback storage.
- Classify empty `{}` as `no-op` or `skipped`, never `useful`.
- Redact raw prompts, secrets, tokens, and sensitive output from receipts.
- Make Doctor distinguish launcher-only, script-entered, unresolved, useful,
  skipped, failed, blocked, and circuit-open outcomes.
- Record live app-server hook notifications and optional local OTLP metrics as
  separate future telemetry layers, not as substitutes for ACC-owned receipts.
- Do not merge UI/live events, OTLP metrics, and ACC receipts into one false
  pass.
- Add installed-runtime regressions for non-Git root, one nested project,
  ambiguous nested projects, context output, state writes, fallback receipts,
  redaction, and empty-output classification.
- Update hook docs, validation, Flow evidence, and Obsidian evidence.
- Do not claim live telemetry proof unless a separate controlled app-server or
  OTLP harness actually captures it.
## Done summary
Nested hook resolver and ACC-owned durable receipts implemented and installed-runtime verified. Live app-server and OTLP telemetry are recorded as separate optional future evidence layers, not required for this core repair.
## Evidence
- Commits:
- Tests: 144 unittest tests OK; compileall OK; Doctor 37 PASS / 0 WARN / 0 FAIL; Flow validate all valid
- PRs: