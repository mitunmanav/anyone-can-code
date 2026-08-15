---
name: cost-guard
description: "Use when user asks cheap vs strong model, Luna/Terra/Sol, or cost tips. Soft tips only — ACC cannot force Codex model picker."
---

# Cost guard

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$cost-guard` for **soft** model-tier tips. Explicit only — do not auto-fire.

## Honesty (always say)

**ACC cannot force Codex model picker.**  
User picks model in Desktop UI, CLI `/model` or `-m`, or `config.toml`.

## Docs (Codex)

- Models: user chooses Sol / Terra / Luna + reasoning effort.
- Skills: teach workflow; no host model API switch.

## Steps

1. Read task words from user.
2. Run helper:
   `python3 "<ACC_PLUGIN_ROOT>/scripts/cost_guard.py" --json <task words>`
   or card:
   `python3 "<ACC_PLUGIN_ROOT>/scripts/cost_guard.py" <task words>`
3. Show card: TIER · PRICE snapshot · TIP · HONESTY.
4. Tell user how to switch (UI slider or `codex -m gpt-5.6-luna|terra|sol`).
5. Optional: `$usage` for token disk status (not model switch).

## Tier map (soft)

| Tier | Model id | Use for |
|------|----------|---------|
| Luna | `gpt-5.6-luna` | clear, repeatable, micro, lint, classify |
| Terra | `gpt-5.6-terra` | everyday feature / bug (default) |
| Sol | `gpt-5.6-sol` | hard, open, security, architecture, research |

Prices = API short-context snapshot in helper. Re-check official pricing before budget.

WEB:

- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/codex/models
- https://openai.com/index/gpt-5-6/

## Rules

- Never claim ACC set the model.
- Never hard-block tools for wrong model.
- Soft tip only. User decides.
- Prefer cheaper tier when task is clear and small.

## Next skill

Token burn check → `$usage`. Build work → `$plan` / `$execute`.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
