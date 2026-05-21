---
name: learn
description: "Captures reinforced learnings through the bundled MCP memory server, with tiny local fallback ledgers only."
---

# Learn

Use `$learn` after verified work, explicit user correction, repeated failure, or when you want to force-save a durable lesson.

Reply rule:

- talk strict caveman only
- keep answer short
- save only strong lesson

## Memory model

Main durable memory lives in the bundled MCP server.

Memory scopes:

- `project`
- `user`
- `shared`

Local project files stay tiny and are only fallback ledgers:

- `.codex/anyone-can-code/learning/`

Suggested tiny local files:

- `signal-ledger.jsonl`
- `mistake-ledger.jsonl`
- short recovery notes only

## Retrieval

- search order: `project -> user -> shared`
- return only top `3-5`
- return summaries only
- no raw logs
- no full chat dump

## Rules

- Auto-learn should write only on durable triggers:
  - explicit correction
  - repeated failure
  - verified success
  - stable preference
  - task-end durable outcome
- `$learn` is manual override: force-save or force-promote when needed.
- Keep provenance, confidence, reinforcement count, and scope with each item.
- Support downgrade and revocation.
- Do not dump all learnings into context.
