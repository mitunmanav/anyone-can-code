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
- what evidence exists
- what passed
- what failed
- what still needs confirmation

## Rule

Built is not verified. Do not collapse those states.
