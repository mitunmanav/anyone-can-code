---
name: verify
description: "Evidence-first verification for code, plans, and repairs. Distinguishes built from verified and records what remains uncertain."
---

# Verify

Reply rule:

- talk strict caveman only
- keep answer short

Use `$verify` before saying the work is complete.

## External tool interop (Superpowers-style)

If front door `tool_interop` has available verify/review/finish bindings, use
those installed skills as evidence helpers. Write the durable record only to
ACC `VERIFICATION.md` (or the binding redirect). Never hand workflow ownership
to the foreign skill.

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

Need eyes on the page. Prefer connected Chrome (`@Chrome`) — safer. The in-app browser
(`@Browser`) can crash the app (Codex bug). Explain plain; user decides; never force.
No Chrome / user OK with mini browser → short preview only, not long test loops.
Missing tool or login → `visual QA unverified`; ask user.

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

Use `verified` only when evidence exists. If a check did not run, say
`implemented` or `blocked`, then name the missing proof.
No "done" without proof: run `python "$PLUGIN_ROOT/scripts/cross_agent_pack.py"`
logic via `claim_done` — product needs real-use path, not unit tests alone.
Do not say interactive work `works` without interaction evidence.
Build, audit, source scan, HTTP 200 are not interaction evidence.
Do not say visual quality, polish, perfect, final, or accepted unless
matching visual QA or user acceptance evidence exists.
Safe wording: `Build passed and HTTP smoke passed. Interactions, visual
quality, and user acceptance unverified.`
Hook repairs: source + unit tests ≠ fixed. Prove hook under cmd.exe and
PowerShell; restart/new-thread proof for Desktop.
Follow `command_guard`. Windows: `npm.cmd`, no Bash-only `||`, Git from repo root.
Verify `usage_checkpoint` before long work: 85% checkpoint, 90% split, 94% stop.
Verify `patch_retry` after a failed patch: reread exact target before retry.
Verify `mechanics_docs_gate`: docs brief before platform mechanics code changes.
Safety receipts for risky/remote work. Release needs installed runtime evidence.

## Headless + GitHub review (native wrap)

- Headless scripts/CI: wrap `codex exec` (default read-only). User decides wider sandbox.
- PR auto-review: Codex cloud + settings Code review; `@codex review` or Automatic reviews.

