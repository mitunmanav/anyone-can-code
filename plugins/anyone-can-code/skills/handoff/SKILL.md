---
name: handoff
description: "Use when moving to a new chat/thread/tool/model or context is near limit. Not for same-thread small questions."
---

# Handoff

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:
- talk strict caveman only
- keep answer short

## Docs (Codex native — wrap only)

- Same Codex session: `codex resume` / `codex resume --last` or `codex exec resume`
- App-server: `thread/resume` (same), `thread/start` (new), `thread/fork` only if user asks fork
- Host move only: Desktop task handoff between computers (remote-connections) — not cross-model
- Do not rebuild rollouts or invent unofficial thread APIs

## Steps

1. Run: `python3 "<ACC_PLUGIN_ROOT>/scripts/build_handoff.py" --project-root .`
   - Big model switch: add `--model <name> --reasoning <low|medium|high>`
   - Writes: `.codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md`
2. Tell user that file is the **any tool / any model** resume bag.
3. Still on Codex?
   - Prefer native resume if same session.
   - New chat: open new task / `thread/start` with the printed prompt whole. Do not trim.
   - No fork unless user says fork.
4. Leaving Codex (other CLI/model): only need that portable file + project folder.
5. Old thread stays readable.

## Model switch

Small change → native model menu under chat (or CLI `/model`).
Big mid-work switch → new chat + this handoff (model+reasoning in prompt). User decides. No invent model API.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
