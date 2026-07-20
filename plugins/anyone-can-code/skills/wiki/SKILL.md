---
name: wiki
description: "Use when user asks what ACC remembers, wiki health, or memory looks broken. Not Codex built-in /memories."
---

# Wiki (ACC notebook)

Reply rule:

- talk strict caveman only
- keep answer short
- ACC wiki only — never Codex `/memories` or `~/.codex/memories/`

## Auto memory (default)

Memory is automatic. Hooks write wants, decisions, open work, and next steps.
SessionStart injects NOW + top lessons. User never needs a memory command in
normal use.

## Where memory lives

```text
.codex/anyone-can-code/memory/
  NOW.md         # live state (auto every turn)
  raw/           # sources; never rewrite
  notes/         # durable pages (auto + backup tools)
  wiki/index.md  # catalog
  wiki/log.md    # what changed
```

## Jobs (backup / repair only)

### Look

Triggers: what did we decide · what do you remember · status of memory

1. Prefer MCP `wiki_brief` then `retrieve_context`.
2. Short answer + note path. No vault dump.
3. `$status` is fine for live Goal/Next.

### Clean

Triggers: clean memory · wiki health · lint wiki · memory broken

1. MCP `lint_wiki` or run `python3 scripts/memory_doctor.py`.
2. Show issues plain. Fix only with user yes (revoke / merge / rebuild).
3. MCP `rebuild_index` after fixes.
4. If doctor says hooks NOT RUNNING: tell user to run `/hooks`, trust
   anyone-can-code, restart Codex (repeat after plugin update).

### Force save (rare backup)

Triggers: user explicitly says force-save this lesson despite auto memory

1. MCP `store_feedback` with kind. Confirm path.
2. Prefer update existing note over near-duplicates.
3. Do **not** tell the user they must save for ACC to remember.

### Raw ingest

Triggers: file this source into raw

1. Need explicit yes.
2. MCP `ingest_raw` with `consent=true`.

## Rules

- AI does not rewrite `raw/`.
- Consent before import / move / overwrite.
- Progressive load: never load whole vault.
- Memory is advisory, not permission.
- Manual tools = backup. Automatic hooks = path.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
