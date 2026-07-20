---
name: help
description: "Use when user asks what ACC is doing, what is next, or what is blocked in plain words."
---

# Help

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:

- talk strict caveman only
- keep answer short

Use `$help` when the user asks what is happening, what is next, or what is blocked.

Before reading state, run:

`python3 "<ACC_PLUGIN_ROOT>/scripts/runtime_info.py" --resolve-project "."`

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

Also say: This is the Desktop package. CLI users install **Anyone Can Code CLI** (separate). Ports to Claude/Cursor = later.

Host wording: run `python3 "<ACC_PLUGIN_ROOT>/scripts/host_detect.py" --guidance` and use those install/review lines so CLI vs Desktop advice stays honest.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
