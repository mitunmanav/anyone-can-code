---
name: settings
description: "Use when changing ACC prefs (talk style, learning, automations, memory path). Not for code tasks."
---

# Settings

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Use `$settings` to inspect or change user preferences.

Reply rule:

- talk strict caveman only
- keep answer short

## Supported preferences

- communication mode: `normal`, `caveman-lite`, `caveman-strict`
- learning preference: enabled or disabled
- automation preference: conservative, balanced, or aggressive
- browser preference: ask or prefer-when-helpful
- learn mode: `trigger-auto`
- memory path: default `.codex/anyone-can-code/memory/notes`, user-changeable
- viewer mode: `none`, `obsidian`, or future `acc-viewer` unavailable
- import sources: explicit selected paths only
- import scope: `ask`, `project`, `user`, or `shared`
- production-repo caution: enabled or disabled

## Storage

- `.codex/anyone-can-code/settings/preferences.json`

## Rule

Communication mode changes surfaced communication only. It does not control hidden reasoning.

When showing or changing communication mode, dry-run tone with the live helper:

```
python3 "<ACC_PLUGIN_ROOT>/scripts/comm_contract.py" caveman-strict "Feature implemented successfully."
```

That script is product path (not tests).

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
