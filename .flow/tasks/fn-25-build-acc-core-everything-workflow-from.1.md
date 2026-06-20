# Add mandatory session audit checklist preflight

## Description
Before any ACC runtime session audit, require the existing Obsidian audit system to be consulted first, not after user correction. The preflight must point to the checklist notes and force complete coverage: user prompts, visible assistant replies, tools, failures, silent failures, hooks, learning, state, compaction, verification, git, and unknowns.

## Acceptance
- Audit workflow names the required Obsidian inputs: 23 Session Audit Master, 30 Session Analyzer Extraction Capability Map, and 36 Manual Usage Session Audit 2026-06-14.
- Audit output must include source file proof, timeline, prompt/response coverage, tool ledger, failure ledger, silent-failure check, learning check, hook check, state-continuity check, compaction check, verification check, git/remote check, and exact/derived/unknown labels.
- Missing checklist use is treated as an audit failure.
- Tests or installed QA prove the checklist gate is visible before audit work starts.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
