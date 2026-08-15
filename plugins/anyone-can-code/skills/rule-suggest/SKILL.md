---
name: rule-suggest
description: "Use when user asks for durable rules from repeated fixes/frustration, or runs $rule-suggest. Not auto every turn — explicit only."
---

# Rule suggest

Reply rule:

- talk strict caveman only
- keep answer short
- **suggest only** — never write without explicit user **yes**

Use `$rule-suggest` when the same fix or frustration keeps showing up and the
user wants a durable note or project rule.

## Job

1. Run helper (read-only):

   `python3 "<ACC_PLUGIN_ROOT>/scripts/rule_suggest.py" --project-root "." --json`

2. Show each suggestion in plain words:
   - what repeated (count + short sample)
   - option A: short ACC wiki/learn note text
   - option B: one `AGENTS.md` bullet

3. Ask user once: wiki/learn note, AGENTS.md bullet, both, or skip?

4. **Only after explicit yes** write the chosen form:
   - wiki/learn → MCP `store_feedback` or `$learn` path (project lesson)
   - AGENTS.md → append one bullet under project `AGENTS.md` (create short
     file if missing; never wipe existing content)

5. If helper returns empty: say "no repeated pattern yet (need 3+ matches)"
   and stop. Do not invent rules.

## Rules

- Explicit skill only — do not auto-fire every turn.
- Never write on propose. User yes first.
- Prefer short bullets. No essay rules.
- Memory is advisory, not permission.
- Distinct from auto `rule_promote` (3+ lessons → permanent `memory/rules.md`).
  This skill is user-pulled Cursor-style suggest for wiki/learn **or** project
  AGENTS.md.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
