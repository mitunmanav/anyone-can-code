# fn-9-build-forensic-session-ledger Build forensic session ledger

## Overview

Build analyzer v3 for the isolated manual session analyzer at:

`C:\Users\Mitun Manav G Y\Desktop\Plugin development\session-analyzer`

The goal is to replace the current unusable Markdown dump with a simple linked Obsidian reading layer backed by complete forensic proof. The analyzer must treat JSONL/NDJSON/JSON-line exports as source truth, preserve every observable event, and produce reviewable outputs for sorting, usage cost, model-behavior signals, compaction loss, caveman compliance, and hidden reasoning metadata.

This is still separate from ACC plugin runtime. It must not touch ACC plugin source, hooks, MCP, installed runtime, GitHub, or background automation.

## Scope

In scope:

- output redesign for `ACC Session Analyzer Dump`
- evidence-first raw ledger from current exported session records
- smart sorting from prompts, cwd/workspace, file paths, tool calls, branch/spec/task names, Obsidian links, and runtime/tool signals
- user review queue and durable correction index
- per-session, per-task, and per-message usage-cost views where evidence allows
- Hidden Reasoning Metadata Analyzer for encrypted reasoning metadata only
- compaction/context-loss analysis
- caveman/token-saving analysis
- tests for parsing, ledger generation, sorting confidence, usage labels, metadata, and cleanup safety
- final conditional cleanup plan for old dump runs after verification and user approval

Out of scope:

- decrypting encrypted hidden reasoning
- claiming access to hidden chain-of-thought
- modifying ACC plugin source
- deleting old dump records before verified replacement output and explicit user approval
- GitHub actions, push, PR, merge, tag, release, publish

## Approach

Build two output layers.

Simple Obsidian reading layer:

```text
00_START_HERE.md
01_READ_THIS_FIRST.md
02_SESSION_REVIEW_QUEUE.md
03_BIG_PICTURE_SUMMARY.md
04_USAGE_COSTS.md
05_HIDDEN_REASONING_METADATA.md
06_COMPACTION_AND_CONTEXT_LOSS.md
07_CAVEMAN_TOKEN_SAVINGS.md
08_SORTED_PROJECT_HISTORY.md
09_FINDINGS_TO_REVIEW.md
sessions/
tasks/
topics/
evidence/
raw-data/
```

Forensic proof layer:

- JSONL ledgers for events, messages, tasks, tools, tokens, hidden reasoning metadata, classifications, and findings
- SQLite tables for fast review/query
- source line hashes and evidence IDs for every parsed/failed source line
- exact/derived/estimated/unknown/impossible label on every derived fact

Smart sorting:

- folder bucket is only a weak input unless it is one of the deliberate official folders
- date folders such as `13` do not decide category
- each session gets suggested category, confidence, evidence, conflicting evidence, and review state
- user corrections become durable reviewed index used by future runs

Usage/cost model:

- exact when direct snapshot fields exist
- derived when before/after snapshots bracket a task/turn/message
- estimated when only nearest snapshots exist
- unknown when evidence is missing
- impossible when data is protected or not exported

Hidden reasoning metadata:

- index encrypted blob line, hash, size, timestamp, turn/task, nearby prompt, nearby token/rate-limit snapshot, following tools/results/failures, compaction link, and outcome
- never decrypt or claim hidden reasoning text

Cleanup gate:

- no deletion until new output is generated, tests pass, current `13` files run successfully, user reviews sorting, accepted index exists, and user explicitly approves exact cleanup target/policy

## Quick commands

- `python -m py_compile session_analyzer.py session_records.py session_metrics.py session_behavior.py session_privacy.py session_reports.py session_index.py`
- `python -m unittest discover -s tests -v`
- `powershell -ExecutionPolicy Bypass -File .\run.ps1 -Label "forensic-ledger-check"`
- `python "C:\Users\Mitun Manav G Y\.codex\plugins\cache\flow-next-marketplace\flow-next\2.0.0\scripts\flowctl.py" validate --spec fn-9-build-forensic-session-ledger --json`

## Acceptance

- [ ] Current `13` JSONL files produce a clean, linked, understandable Obsidian output with `00_START_HERE.md` as the obvious entry point.
- [ ] Raw forensic proof preserves every parsed source line with source file, line number, timestamp when available, event type, evidence ID, and raw-line SHA-256.
- [ ] Prompts/messages are extracted into a private ledger and readable excerpts are linked from session/task reports.
- [ ] Smart sorting assigns suggested categories with confidence, evidence, conflicting evidence, and review state.
- [ ] Date/collection folders such as `13` no longer decide semantic category.
- [ ] User corrections can be stored and future runs reuse the reviewed category index.
- [ ] Usage views report per-session and per-task usage, and per-message usage where evidence supports it, with exact/derived/estimated/unknown labels.
- [ ] Rate-limit pressure timeline is shown from exported rate-limit snapshots.
- [ ] Hidden Reasoning Metadata Analyzer outputs encrypted blob hash/size/source/turn/context and nearby token/tool/outcome evidence, without decrypting or claiming hidden text.
- [ ] Compaction report shows context-compacted events, active-anchor survival/re-anchor status, and likely context-loss risk.
- [ ] Caveman report shows assistant/subagent/report verbosity and likely visible-token savings opportunities.
- [ ] Old dump cleanup is blocked until verified replacement output exists and user explicitly approves cleanup target/policy.
- [ ] Existing analyzer safety boundaries remain: fixed inbox read only, output only under dump root, no ACC plugin runtime, no GitHub, no background automation.
- [ ] Unit tests and py_compile pass.

## References

- Obsidian requirement: `I:\Obsidian vaults\Projects\Anyone Can Code\32 Forensic Session Ledger Output Redesign Request.md`
- Extraction map: `I:\Obsidian vaults\Projects\Anyone Can Code\30 Session Analyzer Extraction Capability Map.md`
- Caveman/compaction strategy: `I:\Obsidian vaults\Projects\Anyone Can Code\31 Caveman and Compaction Token Strategy.md`
- Structured notebook evidence: `I:\Obsidian vaults\Projects\Anyone Can Code\29 Session Analyzer Structured Notebook Upgrade.md`
- Analyzer repo: `C:\Users\Mitun Manav G Y\Desktop\Plugin development\session-analyzer`
- Fixed inbox: `C:\Users\Mitun Manav G Y\Desktop\SESSION ANALYSER MD FILES`
- Dump root: `I:\Obsidian vaults\Projects\ACC Session Analyzer Dump`
