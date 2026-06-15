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
- evidence levels: implemented, source inspected, automated tests, build,
  dependency audit, HTTP smoke, interaction test, visual QA, user accepted
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
Do not say user-facing interactive work `works` unless interaction evidence
exists. Build, audit, source scan, and HTTP 200 are not interaction evidence.
Do not say visual quality, polish, proper, perfect, final, or accepted unless
the matching visual QA or user acceptance evidence exists.
Use safe wording such as:
`Build passed and HTTP smoke passed. Interactions, visual quality, and user
acceptance unverified.`
For hook repairs, source edits and unit tests are not enough for a fixed claim.
Hook launcher repairs must also prove the installed hook command works under
both `cmd.exe /c` and PowerShell outer-shell execution, because Codex Desktop
may launch Windows hooks through either shell boundary.
Require installed-runtime restart or new-thread proof before saying the hook
behavior is fixed in Codex Desktop.
For command or tool work, verify the returned `command_guard` was followed.
On Windows PowerShell, evidence must show `npm.cmd` instead of `npm`, no
Bash-only `||`, and Git commands run from resolved repo root. If repo root,
shell, or failed command output is missing, keep the result unverified.
Verify `usage_checkpoint` before long-running or high-usage work. If primary
usage reached 85%, evidence must show a checkpoint. If it reached 90%, evidence
must show a split or explicit stop. If it reached 94%, evidence must show
stop-now or explicit user choice to continue.
Verify `patch_retry` after edit failures. If there was a failed patch, evidence
must show the exact target was reread before retry. If repeated failed patch
attempts reached the retry limit, evidence must show stop/replan instead of
another retry.
Verify `mechanics_docs_gate` for platform mechanics changes. Evidence must
include a docs brief from official docs/source before code, or controlled proof
with uncertainty recorded when docs/source are missing. Session traces alone do
not prove platform mechanics.
For risky or remote actions, verify the safety receipt exists and records exact
approval, rollback if needed, sandbox context, and remote authority.
Before closing original guardrail or release-readiness work, verify installed
runtime evidence exists. Source-only tests do not prove Codex Desktop behavior.
