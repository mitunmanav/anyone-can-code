---
name: efficiency
description: "Use when user wants ACC cheap/fast lean mode (less inject, soft cheaper-model tips). Not for code tasks."
---

# Efficiency

Reply rule:

- talk strict caveman only
- keep answer short

Turn ACC **cheap and fast** without dropping honesty (goal memory, fail-closed gates stay).

## Turn ON

Any one:

1. Env: `ACC_EFFICIENCY=1` (or `true` / `yes`)
2. Env legacy lean: `ACC_LOAD_LEAN=1` (same effect; unified)
3. Prefs: set `lean: true` (or `efficiency: true`) in  
   `.codex/anyone-can-code/settings/preferences.json`

Example prefs patch (via `$settings` or hand edit):

```json
{
  "lean": true
}
```

Helper (flags only — no host model force):

```
python3 "<ACC_PLUGIN_ROOT>/scripts/efficiency_mode.py"
```

## What changes when ON

| Flag | Effect |
|------|--------|
| lower inject cap | ~3200 chars soft cap (default ~5500) |
| skip Tier C | no host/loops/obs parade in SessionStart |
| skip verbose receipts | no empty "What AI did" parade on lean path |
| prefer short skills | inject reminds progressive + short skill prompts |
| model tip | soft cheaper-label tip from ledger (Luna/mini class) |

**Still always on:** Tier A core (style, NOW, ENFORCE, proof, mistakes). Honesty first.

## Soft model tip only

GPT-5.6 family labels (spirit): **Sol** full · **Terra** mid · **Luna** cheap.

ACC may **suggest** a cheaper model label from the project ledger.  
ACC does **not** control Codex host model picker APIs. Soft tip only. Never claim it switched models.

## Turn OFF

- Unset `ACC_EFFICIENCY` and `ACC_LOAD_LEAN`
- Prefs: `"lean": false` or remove the key
- Restart thread so SessionStart reloads

## When NOT to use

- Hard debug / security / deploy proof needs full inject
- User asked for max context / full loops parade

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
