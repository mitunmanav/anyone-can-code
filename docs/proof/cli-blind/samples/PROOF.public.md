# ACC CLI Blind Proof (public)

**Date:** 2026-07-23  
**Overall:** PASS  
**Host:** Codex CLI only  
**Model:** gpt-5.4-mini  
**Reasoning:** low  
**Plugin:** Anyone Can Code 2.0.0-beta.5  

## What was tested

Strict-blind scenario pack (plain English only — no `$skill` names, no coaching).

Medium product story: local **habit tracker** (Python).

## Results (honest)

| Area | Result |
|------|--------|
| Overall | **PASS** |
| Core product built | PASS |
| SessionStart + Stop hooks | PASS |
| Memory write + later recall | PASS |
| Safety (`curl \| bash` hard block) | PASS |
| Doctor | PASS (0 FAIL) |
| Portable handoff artifact | PASS |
| Skills auto-observed | execute, resume, verify, handoff |
| Many other skills | **NOT PROVEN** (expected under pure blind) |
| Compact / subagent hooks | **NOT PROVEN** |

**Matrix counts:** PASS 14 · FAIL 0 · NOT PROVEN 22

## How to re-run

```bash
# from ACC worktree
python3 docs/proof/cli-blind/run_proof.py --dry-parse
python3 -m pytest docs/proof/cli-blind/tests -q
python3 docs/proof/cli-blind/run_proof.py --run-id <id>
```

See [docs/proof/cli-blind/README.md](../README.md).

## Privacy

This public report is **redacted**:

- No home directory paths  
- No machine usernames  
- No session stderr dumps  
- No auth or config secrets  

Full local runs may create `artifacts/` (gitignored). Do not commit them.

## Bias notes (transparency)

- Automation used Codex `exec` with sandbox and hook-trust flags suitable for unattended runs; flags are disclosed in local PROOF files.  
- Pure blind does **not** claim every skill fired.  
- Independent re-runs may vary by model/host.

## Rating (maintainer note)

Blind score **7/10**: strong core path; incomplete skill matrix under pure blind.
