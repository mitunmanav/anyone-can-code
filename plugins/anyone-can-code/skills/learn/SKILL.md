---
name: learn
description: "Captures reinforced learnings through portable Markdown memory, with tiny local fallback ledgers only."
---

# Learn

Use `$learn` after verified work, explicit user correction, repeated failure, or when you want to force-save a durable lesson.

Reply rule:

- talk strict caveman only
- keep answer short
- save only strong lesson

## Memory model

Main durable memory lives in portable linked Markdown. Bundled MCP is the access
interface.

Memory scopes:

- `project`
- `user`
- `shared`

Local project files stay tiny and are only fallback ledgers:

- `.codex/anyone-can-code/learning/`

Markdown memory lives under:

- `.codex/anyone-can-code/memory/notes/`

Rebuildable index lives under:

- `.codex/anyone-can-code/memory/index/`

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
- no hidden import of existing session files

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
- Existing session files need explicit selected source, backup or snapshot,
  dedupe, provenance, scope label, and receipt before import.
- Repeated import of same content must skip, not reinforce. Failed import must
  roll back Markdown and retain source.
