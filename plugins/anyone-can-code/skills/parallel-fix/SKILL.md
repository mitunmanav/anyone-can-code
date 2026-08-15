---
name: parallel-fix
description: "Use when many pytest files fail and user wants parallel fix. Shard by file, spawn one read-write subagent per file, re-run suite. Not for 1-file fails, not auto."
---

# Parallel fix

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$parallel-fix` only when **many test files** fail. Explicit skill — do not auto-fire.

## Docs (Codex)

Subagents: spawn specialized agents in **parallel**, collect summaries.
Skill/AGENTS can request fan-out. **One write owner per file** — never two agents on same path.
Wait for all shards before full re-run.

## Steps

1. **Run suite** (or use last pytest log). Capture full output.
2. **Shard files:**
   `python3 "<ACC_PLUGIN_ROOT>/scripts/parallel_fix.py" --json`
   (pipe log on stdin, or pass log path).
3. **Gate:**
   - 0 files → stop. Say green or no parse.
   - 1 file → use `$fix` serial. No fan-out.
   - 2+ files → continue.
4. **Spawn one subagent per file** (read-write). Prompt each:
   - Fix **only** this file + its direct tests.
   - Do not touch other failing files.
   - Re-run that file's tests; return short card: file / pass-fail / what changed.
5. **Wait all.** Merge cards.
6. **Re-run full suite.** Fresh evidence only.
7. **Report card** (main thread):

```
WHERE: parallel-fix
SHARDS: N files
FIXED: …
STILL FAIL: …
SUITE: pass|fail (command + counts)
NEXT: $verify or $fix serial leftovers
```

## Rules

- No "all fixed" without **full suite** re-run this turn.
- Same file in two shards → illegal. Dedupe first.
- Shared module both need → stop fan-out; serial `$fix`.
- Token heavy: cap shards if user budget tight (say so; ask).
- Windows: `python`/`pytest` from repo root; no Bash-only glue.

## Next skill

Next: `$verify` on pass. Leftovers → `$fix` serial. Optional `$learn`.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
