# Simplify Session Analyzer Reports and Findings

## Status

On hold. Future analyzer work only. Do not implement until user explicitly resumes this spec.

## Purpose

Make each analyzed Codex session understandable to a non-technical reader while preserving deep evidence for ACC development and development-system improvement.

## User Requirements

- Current analyzer output is too complex and split across too many separate reports.
- Technical depth may remain in the evidence layer when it helps plugin or development-system improvement.
- Each session needs a meaningful plain-language name based on what task actually happened, not only a numeric session, turn, or task ID.
- Each session report must explain what worked.
- Each session report must explain what failed.
- Each session report must identify what appears to have silently broken or regressed.
- Each session report must show uncertainty when evidence cannot prove an outcome.
- Caveman, compaction, token usage, hidden-reasoning metadata, sorting, tools, failures, and other findings should be combined into one final report for that session.
- Separate specialist files may remain as supporting evidence, but user should not need to open them to understand the session.
- Findings should be useful for improving ACC plugin behavior and the development system itself.

## Required User-Facing Shape

One primary final report per session should answer:

1. What was this session trying to do?
2. What should this session be called?
3. What work was completed?
4. What worked?
5. What did not work?
6. What silently broke, regressed, or became inconsistent?
7. What remains uncertain or needs review?
8. What tools, files, and systems were involved?
9. Where was time or token usage wasted?
10. Did compaction or instruction loss affect the result?
11. Did caveman communication survive?
12. What lessons should improve ACC or its development workflow?
13. What exact evidence supports each finding?

## Naming Rules

Generate a short session title from strongest available evidence:

- user request and task wording
- Flow spec/task title
- workspace and repository
- files changed
- tool activity
- visible outcome

Keep original IDs as secondary proof fields. Never replace provenance.

## Outcome Rules

Classify findings with evidence labels:

- worked
- failed
- silently-broke
- partial
- uncertain
- not-attempted

Every finding must link to source evidence and state whether it is exact, derived, estimated, or unknown.

## Report Consolidation Rule

Primary session report combines all important findings. Specialist reports remain optional supporting evidence only. Root navigation should lead to session final reports first.

## Boundaries

- Analyzer remains separate from ACC plugin source.
- Do not change ACC plugin source for this work.
- Do not delete old dump output.
- Cleanup still requires user review and explicit approval of exact target and policy.
- Hidden reasoning stays metadata-only; no decryption claim.
- No implementation while this spec is on hold.

## Acceptance Direction

Future implementation is acceptable only when a non-technical reader can open one report, understand the session without interpreting numeric IDs, see worked/failed/silent-break findings, and follow evidence links when deeper proof is needed.
