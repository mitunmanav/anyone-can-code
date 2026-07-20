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

**Iron law:** no "done", "works", "fixed", or "perfect" without named evidence from this skill (command, file, output, or real use). Built ≠ verified. Tests are part of verify — run them when they exist.

## Output

Write a verification record to:

- `.codex/anyone-can-code/artifacts/VERIFICATION.md`

Include:

- what was checked
- evidence levels: implemented, source inspected, automated tests, build,
  dependency audit, HTTP smoke, interaction test, visual QA, user accepted
- result: pass, fail, or pass with uncertainty
- exact evidence: command, file, output, or captured behavior
- what passed / failed (incl. silent later) / still uncertain
- next step

## Terminal evidence

Codex reads the integrated terminal (Cmd+J). For running servers or builds:
read the terminal output NOW, before any claim. Server "works" needs a live
terminal line proving it serves; a failed or silent terminal = not working.
Never claim from memory or from an old run. Timeout (exit 124) = NOT ready.

## Browser visual QA (web products)

Need eyes on the page. Run first:

```
python3 "<ACC_PLUGIN_ROOT>/scripts/browser_policy.py"
```

Prefer connected Chrome (`@Chrome`) — safer. Built-in in-app browser (`@Browser`) can crash (Codex bug).
Explain plain; user decides; never force. Signed-in/login pages may need Chrome. Missing tool → `visual QA unverified`.

## Review handoff + ship gate

After code changes, send user to review:
- **CLI:** `/review` (working tree review; no auto-edit).
- **Desktop:** review pane (green = added, red = removed) or `/review`.
User can revert any file they dislike. Git repos only; no repo — offer to
create one. Before ship/deploy: review + security gate
(`scripts/security_gate.py`) + explicit user YES. Never force ship.

## Rule

Built is not verified. Do not collapse those states.
Only use these workflow states: `in scope`, `designed`, `approved`,
`implemented`, `verified`, `blocked`, `deferred`.

Use `verified` only with evidence. Missing check → `implemented`/`blocked` + name gap.
Product "works" needs real-use path, not unit tests alone. HTTP 200 ≠ interaction proof.
Visual/polish/accepted only with visual QA or user acceptance evidence.
Windows: `npm.cmd`, no Bash-only `||`, Git from repo root. Risky ship needs safety receipts.
Verify `command_guard` on shell/Git. Verify `usage_checkpoint` before long work: 85% checkpoint, 90% split, 94% stop.
Verify `patch_retry` after a failed patch: reread exact target before retry.
Verify `mechanics_docs_gate`: docs brief before platform mechanics code changes.

## Next skill

Next: if fail → `$fix` then re-verify. If pass → optional `$learn`. Never claim done without evidence here.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
