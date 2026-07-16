---
name: settings
description: "Manages communication mode, learning preference, and automation preference for Anyone Can Code."
---

# Settings

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
python "$PLUGIN_ROOT/scripts/comm_contract.py" caveman-strict "Feature implemented successfully."
```

That script is product path (not tests).
