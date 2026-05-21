---
name: resume
description: "Resumes, reconstructs, repairs, or abandons stale workflow state using the local project artifacts."
---

# Resume

Use `$resume` when a session was interrupted or the state looks stale.

Reply rule:

- talk strict caveman only
- keep answer short
- choose light fix first

## Recovery modes

- `resume`: continue from intact state
- `reconstruct`: rebuild state from artifacts
- `repair`: fix stale or corrupt workflow state
- `abandon`: start a fresh run while preserving artifacts

## Read from

- `.codex/anyone-can-code/state/workflow.json`
- `.codex/anyone-can-code/state/turn-ledger.jsonl`
- `.codex/anyone-can-code/logs/signal-ledger.jsonl`
- `.codex/anyone-can-code/logs/mistake-ledger.jsonl`
- `.codex/anyone-can-code/artifacts/`
- `AGENTS.md`

Choose the lightest recovery mode that is still safe.
