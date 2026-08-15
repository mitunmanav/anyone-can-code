---
name: memory-hygiene
description: "Use when user wants clean ACC wiki memory: age old notes, flag secrets, block full-chat dumps. Not Codex /memories. Explicit only."
---

# Memory hygiene (ACC wiki)

Reply rule:

- talk strict caveman only
- keep answer short
- **ACC wiki only** — never Codex `/memories` or `~/.codex/memories/`
- **report first** — no archive/scrub write without explicit user **yes**

## Job

1. Run helper (read-only):

   `python3 "<ACC_PLUGIN_ROOT>/scripts/memory_hygiene.py" --project-root "." --json`

2. Show plain card:
   - note count
   - stale (≥28 days, Copilot-style unused age)
   - secret flags (values never printed raw)
   - full-chat dump flags

3. Suggest only:
   - stale → archive note or refresh summary
   - secret → scrub / revoke note
   - full chat → replace with short lesson (never keep transcript)

4. **Only after explicit yes** do the chosen fix (MCP `revoke_memory` /
   short `$learn` rewrite). Helper itself never writes.

5. Before any new durable note: call

   `python3 ".../memory_hygiene.py" --validate-text "..."`  

   Reject `full_chat` and `secret`. Store short facts only.

## Rules

- Explicit skill only — not every turn.
- Never store full chat in wiki notes.
- Never echo raw secrets in replies.
- Memory is advisory, not permission.
- Distinct from `$wiki` look/repair and `$learn` force-save.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
