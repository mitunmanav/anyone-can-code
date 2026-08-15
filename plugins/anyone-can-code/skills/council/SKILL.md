---
name: council
description: "Use when user wants multi-view review (correctness / safety / honesty) before ship. Read-only. Not a ship gate — still run $verify."
---

# Council

Reply rule:

- talk strict caveman only
- keep answer short

Use `$council` for a **multi-view check** of recent work or a named scope.
**Inside ACC only.** Not an external council product. `$bridge` stays for other plugins.

## HARD LAW

1. **Not a ship gate.** Council is advice only. Still run `$verify` before done/works/fixed.
2. **Read-only.** No write, patch, commit, push, install, deploy, or state mutation.
3. **Does not replace `$verify`.** No pass/fail ship claim from this skill alone.
4. **Does not replace `$bridge`.** Other plugins still go through `$bridge`.

## When to use

- User asks for council / multi-view / second opinion.
- Before ship, want correctness + safety + honesty views.
- Plan or diff feels one-sided; need push-back.

## When NOT to use

- Claiming done → `$verify` (evidence).
- Fixing bugs → `$fix` then `$verify`.
- Routing other plugins → `$bridge`.
- Scope change → `$govern`.

## Do this

1. Name the **scope** (files, PR, plan, or “last change”). If unclear, ask one line.
2. Run up to **3** read-only views (parallel subagents OK; max 3):

| View | Ask |
|------|-----|
| **Correctness** | Does it do what was asked? Logic holes? Missing tests? |
| **Safety** | Secrets, destructive paths, unsafe defaults, trust holes? |
| **Honesty** | Overclaim? Fake pass? Missing evidence? Docs vs code lie? |

3. Use **read-only tools only** (read, search, list, status). No edits.
4. If using subagents, say it **literally** (Codex only spawns when told):

```
Spawn a subagent.
Job: <correctness | safety | honesty> review of <scope>
Scope: <exact files/dirs; read-only>
Expected output: 3-6 bullets, file:line if possible, YES/NO risk
Speak caveman style: simple, short, direct, clear YES/NO, no ceremony.
```

All four lines or no spawn. Results return to ACC. You merge.

5. Emit one **caveman card** (see Output). Then stop.

## Output (required card)

```
COUNCIL (not a ship gate — still run $verify)
SCOPE: <one line>
CORRECT: <PASS | RISK | FAIL> — <one line>
SAFE:    <PASS | RISK | FAIL> — <one line>
HONEST:  <PASS | RISK | FAIL> — <one line>
TOP:     <up to 3 bullets; file:line when known>
NEXT:    run $verify | fix X then $verify | ask user
```

Always include the line: **not a ship gate — still run $verify**.

## Rules

- No “ship it” / “done” / “verified” from council alone.
- No silent file changes. Findings only.
- Disagree views → say the conflict; do not force consensus.
- Unknown → `RISK`, not fake PASS.
- Token cost: keep subagent scopes tight; prefer one main pass if scope tiny.

## Next skill

- Findings need proof → `$verify`
- Clear bug → `$fix` then `$verify`
- Other plugin may help → `$bridge` (ACC still owns workflow)

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
