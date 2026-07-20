---
name: verify
description: "Use when about to claim done/works/fixed, or user asks test/check/prove. Run evidence; not for pure planning chat."
---

# Verify

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Reply rule:

- talk strict caveman only
- keep answer short

Use `$verify` before saying the work is complete.

## HARD-GATE / iron law

No "done", "works", "fixed", or "perfect" without **named evidence from this
skill** (command, file, output, or real use) run **now**. Built ≠ verified.
Tests are part of verify — run them when they exist.

If you have not run the check in this turn, you cannot claim pass.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "Should pass" / "probably fine" | Run the command. Read output. |
| "I already tested earlier" | Old run ≠ now. Fresh check. |
| "Looks correct in the diff" | Diff ≠ run. |
| "Unit tests alone prove product works" | Need real-use path too when product path exists. |
| "Great!" before any command | Satisfaction after evidence only. |

## Output

Write a verification record to `.codex/anyone-can-code/artifacts/VERIFICATION.md`
(what checked, result, exact evidence, next step). Full fields:
`references/verify-details.md`.

## Terminal evidence

For running servers or builds: **read the terminal output** NOW before any
claim. Never claim from memory or from an old run. Timeout = NOT ready.

## Browser visual QA (web)

Prefer Chrome (`@Chrome`) — safer; in-app browser (`@Browser`) can crash.
Explain plain; user decides; never force. Signed-in/login may need Chrome.
Missing tool → visual QA **unverified**. Run
`python3 "<ACC_PLUGIN_ROOT>/scripts/browser_policy.py"` first when needed.

## Review handoff + ship gate

After code changes: Desktop **review pane** (green = added, red = removed) or
`/review`. User can **revert** any file. Before ship: review +
`scripts/security_gate.py` + user YES.

## Rule

Built is not verified. States: `in scope`, `designed`, `approved`,
`implemented`, `verified`, `blocked`, `deferred`. Use `verified` only with
evidence.

Windows: `npm.cmd`, no Bash-only `||`, Git from **repo root**.
Verify `command_guard` on shell/Git.
Verify `usage_checkpoint` before long work: **85%** checkpoint, **90%** split, **94%** stop.
Verify `patch_retry` after a **failed patch**: **reread** exact target before retry.
Verify `mechanics_docs_gate`: **docs brief** before **platform mechanics** code.

## Next skill

Next: if fail → `$fix` then re-verify. If pass → optional `$learn`. Never claim
done without evidence here.

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
