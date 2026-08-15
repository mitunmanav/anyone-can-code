---
name: you-brain
description: "Use when user wants mine past Codex sessions into a compact YOU profile, preview you-brain, or apply YOU.md. One-shot local mine — no AI, no embedder."
---

# You-Brain ($you-brain)

One-shot **local** mine of Codex `rollout-*.jsonl` → compact user brain.

Reply rule:

- talk strict caveman only
- keep answer short

## Hard locks

- **No model API** during mine
- **No embedder** v1
- **No native Codex memories** — ACC user drawer only
- **Default dry-run** — preview only
- **Apply only** when user says apply / yes / `--apply`
- Soft model tips show **n + confidence** — never force model switch

## Where data lives

User drawer (taste / profile):

```text
~/.codex/anyone-can-code/user-memory/you-brain/
  raw/facts.jsonl          # L1 append-only
  aggregates/summary.json  # L2 rebuildable
  YOU.preview.md           # always
  YOU.md                   # only after --apply
  ingest-index.json        # skip unchanged
  imports/receipt-*.json
```

Override root: `ACC_USER_MEMORY_ROOT` or script `--memory-root`.

Sessions source: `CODEX_HOME/sessions` then `~/.codex/sessions`.

## Run

Script root: use `ACC_PLUGIN_ROOT` from SessionStart context (hooks inject it).
`PLUGIN_ROOT` is hooks-only — do not assume it in the agent shell.

**Preview (default):**

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/session_mine_super.py" --json
```

**Apply L3 YOU.md (only if user said yes):**

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/session_mine_super.py" --apply --json
```

Useful flags:

- `--sessions-root <dir>` (repeatable)
- `--memory-root <dir>`
- `--max-files 40` `--max-mb 256`
- `--force` re-mine even if unchanged
- `--ledger <path/to/model-ledger.jsonl>` soft tips from ledger
- `--json`

## What to tell user

1. Show receipt: scanned / mined / skipped / api_tokens=0
2. Point at `YOU.preview.md`
3. Ask: apply to `YOU.md`? only on yes run `--apply`
4. Soft tips = advisory; user choice wins

## Not this skill

- Live session notes / `$learn` → learn skill
- Project wiki → wiki skill
- Native Codex `/memories` → stay OFF

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
