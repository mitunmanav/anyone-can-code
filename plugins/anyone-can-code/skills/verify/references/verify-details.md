# Verify details (read when needed)

## Output file

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

Prefer connected Chrome (`@Chrome`) — safer. Built-in in-app browser (`@Browser`)
can crash (Codex bug). Explain plain; user decides; never force. Signed-in/login
pages may need Chrome. Missing tool → `visual QA unverified`.

## Review handoff + ship gate

After code changes, send user to review:

- **CLI:** `/review` (working tree review; no auto-edit).
- **Desktop:** review pane (green = added, red = removed) or `/review`.

User can revert any file they dislike. Git repos only; no repo — offer to
create one. Before ship/deploy: review + security gate
(`scripts/security_gate.py`) + explicit user YES. Never force ship.

## State + platform checks

Built is not verified. Do not collapse those states.
Only use: `in scope`, `designed`, `approved`, `implemented`, `verified`,
`blocked`, `deferred`.

Use `verified` only with evidence. Missing check → `implemented`/`blocked` + name gap.
Product "works" needs real-use path, not unit tests alone. HTTP 200 ≠ interaction proof.
Visual/polish/accepted only with visual QA or user acceptance evidence.

Windows: `npm.cmd`, no Bash-only `||`, Git from repo root. Risky ship needs safety receipts.
Verify `command_guard` on shell/Git. Verify `usage_checkpoint` before long work:
85% checkpoint, 90% split, 94% stop.
Verify `patch_retry` after a failed patch: reread exact target before retry.
Verify `mechanics_docs_gate`: docs brief before platform mechanics code changes.
