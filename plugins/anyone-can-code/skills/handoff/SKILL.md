---
name: handoff
description: "Moves work to a fresh Codex thread with full context: state, memory, git status, style rules. Use when user says move to new chat, new thread, continue elsewhere, or context is near limit."
---

# Handoff

Reply rule:
- talk strict caveman only
- keep answer short

## Steps

1. Run: `python "$PLUGIN_ROOT/scripts/build_handoff.py" --project-root .`
2. Take the printed prompt whole. Do not trim.
3. Use Codex `create_thread` (same project, local env) with that prompt.
4. No `fork_thread` unless user says fork.
5. Tell user: new thread ready, old thread stays readable.
