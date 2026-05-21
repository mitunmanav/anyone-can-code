---
name: fix
description: "Recovery workflow for repeated failures. Uses local turn history, verification output, and overlap checks before retrying or abandoning."
---

# Fix

Use `$fix` when verification keeps failing or the current route needs controlled recovery.

## Inputs

- `.codex/anyone-can-code/state/turn-ledger.jsonl`
- `.codex/anyone-can-code/artifacts/VERIFICATION.md`
- `.codex/anyone-can-code/artifacts/resume-note.md`

## Rules

- Never silently continue after repeated failure.
- Prefer repair guidance before revert-like behavior.
- If user work may overlap with plugin-made changes, pause and surface the conflict.
- Record the recovery outcome in the local artifacts area.
