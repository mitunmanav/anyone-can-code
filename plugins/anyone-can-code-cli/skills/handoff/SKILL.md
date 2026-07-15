---
name: handoff
description: "Moves work to a fresh Codex thread with full context: state, memory, git status, style rules. Use when user says move to new chat, new thread, continue elsewhere, switch model mid-work, or context is near limit."
---

# Handoff

Reply rule:
- talk strict caveman only
- keep answer short

## Steps

1. Run: `python "$PLUGIN_ROOT/scripts/build_handoff.py" --project-root .`
   - Big model switch: add `--model <name> --reasoning <low|medium|high>`
2. Take the printed prompt whole. Do not trim.
3. Use Codex `create_thread` (same project, local env) with that prompt.
4. No `fork_thread` unless user says fork.
5. Tell user: new thread ready, old thread stays readable.

## Model switch

Small change → native model menu under chat (or CLI `/model`).
Big mid-work switch → new chat + this handoff (model+reasoning in prompt). User decides. No invent model API.
