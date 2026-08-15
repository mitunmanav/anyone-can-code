# Proof — park-you-brain (You-Brain v1 skeleton)

**Branch:** `feature/park-you-brain`  
**Scope:** one-shot local mine of Codex `rollout-*.jsonl` → L1/L2 + YOU preview  
**Locks:** no model API · no embedder · no native Codex memories · dry-run default

## Docs topics (Codex first)

| Topic | Takeaway for this feature |
|-------|---------------------------|
| Hooks | Lifecycle only; mine is **offline script**, not a quiet SessionStart dump |
| Memories | Native Codex memories stay **OFF**; ACC two-drawer / user-memory is product brain |
| Sessions disk | Live truth = `~/.codex/sessions/**/rollout-*.jsonl` (or `CODEX_HOME/sessions`) |
| MEMORY-CONTRACT | User drawer for taste (`YOU.md`); project drawer stays project facts |
| Consent | Existing session mine needs explicit apply for L3; preview is default |

## What shipped

| Piece | Path |
|-------|------|
| Miner CLI | `plugins/anyone-can-code/scripts/session_mine_super.py` |
| Skill | `plugins/anyone-can-code/skills/you-brain/SKILL.md` (`$you-brain`) |
| Fixture | `plugins/anyone-can-code/tests/fixtures/you_brain_tiny_rollout.jsonl` |
| Tests | `plugins/anyone-can-code/tests/test_session_mine_super.py` |

### Pipeline

```text
rollout-*.jsonl
  → stream parse (skip corrupt)
  → budgets: max files / max MB
  → ingest-index skip unchanged
  → L1 raw/facts.jsonl
  → L2 aggregates/*.json
  → YOU.preview.md (always)
  → YOU.md only with --apply
  → soft model tip (ledger if present; n + confidence)
```

### Extracted fields (v1)

- model (session_meta / turn_context)
- reasoning_effort (turn_context collaboration settings)
- token_count totals (event_msg)
- task signals (rule keywords on user text)
- user correction hits (rule phrases)

## How to verify

From worktree root:

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_session_mine_super.py -q
```

Manual dry-run against fixture tree:

```bash
python3 plugins/anyone-can-code/scripts/session_mine_super.py \
  --sessions-root /path/to/sessions \
  --memory-root /tmp/you-brain-test \
  --json
# expect: applied=false, YOU.preview.md present, YOU.md absent, token_cost=0
```

Apply (explicit):

```bash
python3 plugins/anyone-can-code/scripts/session_mine_super.py \
  --sessions-root /path/to/sessions \
  --memory-root /tmp/you-brain-test \
  --apply --json
# expect: YOU.md with Status APPLIED
```

## Expected test outcomes

- Parse fixture → model `gpt-5.6-sol`, effort `medium`, tokens, bug-fix + feature signals
- Dry-run → L1 + L2 + preview; no `YOU.md`
- `--apply` → `YOU.md` written
- Second run → ingest-index skips unchanged
- Ledger soft tip → n≥4, conf≤0.85, soft=true
- API token cost always 0

## Out of scope (later slices)

- Continuous live mine on every Stop
- Embeddings / vector search
- Auto-apply YOU.md
- Full chat dump into SessionStart
- Push / merge / release

## PASS criteria for this park slice

1. `pytest … test_session_mine_super.py` green  
2. Script runs with `--json` and reports `token_cost: 0`  
3. Default path does not write `YOU.md` without `--apply`  
4. Native memories policy unchanged (still OFF)
