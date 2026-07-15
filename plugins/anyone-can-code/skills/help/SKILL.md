---
name: help
description: "Reads the local workflow files and explains where the project stands in plain language."
---

# Help

Reply rule:

- talk strict caveman only
- keep answer short

Use `$help` when the user asks what is happening, what is next, or what is blocked.

Before reading state, run:

`python "$PLUGIN_ROOT/scripts/runtime_info.py" --resolve-project "."`

Use returned `project_root`. If status is `ambiguous`, stop and show candidates;
never report root idle state as final and never choose silently.

Read from:

- `.codex/anyone-can-code/state/workflow.json`
- `.codex/anyone-can-code/state/state-current.md`
- `.codex/anyone-can-code/artifacts/resume-note.md`
- `.codex/anyone-can-code/settings/preferences.json`

Explain memory as portable Markdown. If migration/import failed, name rollback
receipt and say original source remains. Never describe JSONL as current durable
memory.

Answer in plain language, not internal jargon.
When explaining the active route, use the same entry-mode and route names from
`scripts/front_door.py`. Never expose development-system audit or promotion
terms as product workflow.

Also say: Desktop or CLI both work (same plugin). ACC can self-audit itself
with `expand_pack.py self-audit`. Ports to Claude/Cursor = later.
