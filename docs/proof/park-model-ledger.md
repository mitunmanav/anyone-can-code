# Proof — park model ledger (task_type)

**Branch:** `feature/park-model-ledger`  
**Date:** 2026-08-03  
**Scope:** half-wired `model_ledger` — write stuck `task_type="general"` while read used `workflow.route`.

## Codex docs first

- Hooks common input includes `model` (Codex extension, active model slug).
- `Stop` / `SessionStart` are supported hook events; ACC uses them for save/load.
- No invented host model-switch API — ledger is **advice only** (recommend text in SessionStart context).

Command:

```bash
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" hooks
```

## Problem

| Path | Before | Bug |
|------|--------|-----|
| `save_session.record_session_model_outcome` | always `"general"` | write never matched real work |
| `load_session.build_context` | `workflow.route or "general"` | empty route → default; mismatch with writes |
| reasoning on record | omitted | weaker future tips |

## Fix

1. **`classify_task_type` / `task_type_from_session`** in `plugins/anyone-can-code/scripts/model_ledger.py`  
   Deterministic from: route aliases → skill names → tool names → user/summary keywords → signals → `general`.
2. **`save_session`** records classified `task_type` + payload reasoning (not hardcoded general).
3. **`load_session`** classifies the same way before `recommend_model` / reasoning tip.
4. **`recommend_model` / `recommend_reasoning`** normalize aliases (`feature-request` → `feature`) and filter ledger rows by real task type.

## Files

- `plugins/anyone-can-code/scripts/model_ledger.py`
- `plugins/anyone-can-code/hooks/scripts/save_session.py`
- `plugins/anyone-can-code/hooks/scripts/load_session.py`
- `plugins/anyone-can-code/tests/test_model_ledger.py`
- `docs/proof/park-model-ledger.md` (this file)

## Proof command

```bash
cd "/home/mitun/anyonecancode development/.worktrees/feature-park-model-ledger"
python3 -m pytest plugins/anyone-can-code/tests/test_model_ledger.py -q
```

## Result

```
............                                                             [100%]
12 passed
```

Covers:

- classify from keywords / skills / tools / route / signals
- multi-type recommend isolation (bug-fix vs feature vs research)
- session Stop write not stuck on `general`
- bug-fix route + reasoning on record
- recommend_reasoning not always high

## Not done (out of lane)

- Force-switch Codex active model (host has no ACC API for that).
- Push / merge to main.
