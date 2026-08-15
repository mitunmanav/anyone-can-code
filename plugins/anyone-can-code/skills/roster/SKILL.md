---
name: roster
description: "Use when user wants a Codex subagent role list (explorer/worker/reviewer) as paste-ready prompts. Explicit only — prompts only, never write agent TOML."
---

# Roster

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short
- **prompts only** — never write `.codex/agents/*.toml`

Use `$roster` when the user wants a suggested subagent team for parallel work.

## Docs (Codex + Copilot analog)

- Codex built-ins: `explorer` (read), `worker` (implement), `default` (fallback).
- Custom agents: user-owned TOML under `~/.codex/agents/` or `.codex/agents/`
  (`name`, `description`, `developer_instructions`).
- Skill/AGENTS may request fan-out; Codex spawns when told literally.
- Copilot analog: agent profiles = role prompts — same idea, different host.
- ACC suggests spawn text. User pastes / asks spawn. ACC does **not** install agents.

## Steps

1. Run helper:

   `python3 "<ACC_PLUGIN_ROOT>/scripts/subagent_roster.py" --json --goal "<job>" --scope "<paths>"`

   Optional: `--roles explorer,worker,reviewer`

2. Show each role: when / scope / paste-ready block.

3. Spawn only if user wants. Each spawn must be literal:

```
Spawn a subagent.
Agent: <explorer|worker|reviewer>
Job: <one exact task>
Scope: <exact files/dirs; read-only unless stated>
Expected output: <exact shape>
Speak caveman style: simple, short, direct, clear YES/NO, no ceremony.
```

4. Wait for all. Merge summaries on main thread. Verify before "done".

## Rules

- Explicit skill only — do not auto-fire.
- Max ~3 parallel; one write owner per path.
- Explorer + reviewer = read-only. Worker = one bounded write job.
- Never claim TOML written. Optional snippet = user paste only.
- Output returns to ACC for verification.

## Next skill

Next: `$plan` / `$execute` / `$verify` / `$fix` as fit. Optional `$learn`.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
