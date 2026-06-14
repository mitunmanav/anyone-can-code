---
name: verify
description: "Evidence-first verification for code, plans, and repairs. Distinguishes built from verified and records what remains uncertain."
---

# Verify

Use `$verify` before saying the work is complete.

## Verification goals

- confirm that the requested behavior exists
- confirm that relevant checks ran
- surface remaining uncertainty
- decide whether to continue, repair, or ship

## Output

Write a verification record to:

- `.codex/anyone-can-code/artifacts/VERIFICATION.md`

Include:

- what was checked
- result: pass, fail, or pass with uncertainty
- exact evidence: command, file, output, or captured behavior
- what passed
- what failed, including silent failure discovered later
- what remains uncertain or unverified
- next step

## Rule

Built is not verified. Do not collapse those states.
Only use these workflow states: `in scope`, `designed`, `approved`,
`implemented`, `verified`, `blocked`, `deferred`.

Use `verified` only when evidence exists. If a check did not run, say
`implemented` or `blocked`, then name the missing proof.
For hook repairs, source edits and unit tests are not enough for a fixed claim.
Require installed-runtime restart or new-thread proof before saying the hook
behavior is fixed in Codex Desktop.
For risky or remote actions, verify the safety receipt exists and records exact
approval, rollback if needed, sandbox context, and remote authority.
Before closing original guardrail or release-readiness work, verify installed
runtime evidence exists. Source-only tests do not prove Codex Desktop behavior.
