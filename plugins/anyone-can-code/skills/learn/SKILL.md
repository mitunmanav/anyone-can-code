---
name: learn
description: "Captures reinforced learnings through portable Markdown memory, with tiny local fallback ledgers only."
---

# Learn

Memory is automatic (hooks write wants, decisions, corrections, open work).
Use `$learn` only as a **backup** force-save or force-promote — never as the
normal path. Do not tell the user they must run `$learn` to be remembered.

Reply rule:

- talk strict caveman only
- keep answer short
- auto path first; manual only when user asks to force-save

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

Human wiki catalog + log:

- `.codex/anyone-can-code/memory/wiki/index.md`
- `.codex/anyone-can-code/memory/wiki/log.md`

Raw sources (never rewrite):

- `.codex/anyone-can-code/memory/raw/`

Rebuildable machine index lives under:

- `.codex/anyone-can-code/memory/index/`

Native Codex memories stay OFF. Prefer `$status` to see what ACC remembers;
`$wiki` / `memory_doctor.py` only for look / repair.

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
- front door must run `scripts/memory_preflight.py` after active-project
  resolution and before asking, planning, choosing specialists, browser/server
  work, or tool work
- every routed turn must show `Relevant memory used: ...` or
  `Relevant memory used: none found`
- update, restart, and new thread must not weaken recall; memory path comes
  from project preferences

## About-you profile

- user explicitly corrects skill level, reply taste, or stack choice ->
  `user_model.record_correction`. Never guess these. Shown at session start.

## Rule promotion

- lesson seen 3+ times in notes: propose once — "make permanent rule? yes/no"
- user says yes -> `rule_promote.approve` writes `memory/rules.md`, shown every session start
- user says no -> stays a normal lesson
- never promote without explicit yes

## Rules

- Auto-learn is hook-owned (UserPromptSubmit + Stop promote rules + signals).
- `$learn` is manual override only: force-save or force-promote when needed.
  Never required for normal memory.
- Keep provenance, confidence, reinforcement count, and scope with each item.
- Support downgrade and revocation.
- Treat memory as advisory context, never truth or permission.
- Do not dump all learnings into context.
- Existing session files need explicit selected source, backup or snapshot,
  dedupe, provenance, scope label, and receipt before import.
- Repeated import of same content must skip, not reinforce. Failed import must
  roll back Markdown and retain source.
