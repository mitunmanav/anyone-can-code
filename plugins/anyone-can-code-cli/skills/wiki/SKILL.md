---
name: wiki
description: "Save, ask, or clean ACC project wiki memory (Karpathy-style notes + index + log). Use when user says remember, save this, what did we decide, recall, clean memory, or wiki health. Never uses Codex built-in memories."
---

# Wiki (ACC notebook)

Reply rule:

- talk strict caveman only
- keep answer short
- ACC wiki only — never Codex `/memories` or `~/.codex/memories/`

## Where memory lives

```text
.codex/anyone-can-code/memory/
  raw/           # sources; never rewrite
  notes/         # durable pages
  wiki/index.md  # catalog
  wiki/log.md    # what changed
```

## Jobs

### Save

Triggers: remember · save this · file this · decision · lesson

1. Ask scope if unclear: project (default) vs user taste only.
2. MCP `store_feedback` with kind (`decision` / `lesson` / `failure` / …).
3. Confirm path. Index + log update automatically.
4. Prefer update existing note over near-duplicates.

### Ask

Triggers: what did we decide · recall · remember when · wiki

1. Prefer MCP `wiki_brief` then `retrieve_context` with the question.
2. Short answer + note path. No vault dump.

### Clean

Triggers: clean memory · wiki health · lint wiki

1. MCP `lint_wiki`.
2. Show issues plain. Fix only with user yes (revoke / merge / rebuild).
3. MCP `rebuild_index` after fixes.

### Raw ingest

Triggers: file this source into raw

1. Need explicit yes.
2. MCP `ingest_raw` with `consent=true`.
3. Then optional Save for a wiki summary of that source.

## Rules

- AI does not rewrite `raw/`.
- Consent before import / move / overwrite.
- Progressive load: never load whole vault.
- Memory is advisory, not permission.
