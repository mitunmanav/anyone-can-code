# Proof — park raw + script mine v1

**Branch:** `feature/park-raw-mine`  
**Date:** 2026-08-03  
**Law:** ADD-ONLY. Keep notes/wiki/learn/two drawers. No full chat in SessionStart.

## Codex docs (first)

Source: `codex docs/read-docs.py` → Hooks page (`developers.openai.com/codex/hooks`).

| Event | Fields used | Wire |
| --- | --- | --- |
| `UserPromptSubmit` | `prompt`, `turn_id`, `session_id` | `guard.py` → `raw_capture.capture_user_prompt` |
| `Stop` | `last_assistant_message`, `turn_id`, `stop_hook_active` | `save_session.py` → `raw_capture.capture_assistant_turn` + `raw_mine.mine_raw` |
| `SessionStart` | inject only NOW/wiki brief/caps | **unchanged** — no raw dump |

`Stop` must emit JSON on stdout (existing `save_session` contract kept).

ACC keeps own wiki/notes; native Codex `/memories` stay off product path.

## Design source

`/home/mitun/anyonecancode development/.grok/handoffs/PARKED_MEMORY_RAW_MINE.md` (read only).

Line: raw gold → scripts/rules mine → notes → same small inject.

## What landed

| Piece | Path |
| --- | --- |
| Capture | `plugins/anyone-can-code/hooks/scripts/raw_capture.py` |
| Mine | `plugins/anyone-can-code/scripts/raw_mine.py` |
| User wire | `hooks/scripts/guard.py` (UserPromptSubmit) |
| Assistant + mine wire | `hooks/scripts/save_session.py` (Stop) |
| Tests | `plugins/anyone-can-code/tests/test_raw_capture_mine.py` |

### Capture format (`memory/raw/turns.jsonl`)

One JSON object per line:

- `schema_version`, `timestamp`, `role` (`user` \| `assistant`)
- `text` (redacted via `memory_core.scrub`)
- `content_hash`, `secret_redacted`, `source`
- `session_id`, `turn_id`

Append-only. Project drawer only. No rotate (immutable gold).

### Mine rules (v1)

Pure Python on **user** role turns:

- preference: always/never/prefer/from now on/caveman short
- decision: use X for / switch to / decided
- lesson: don't do / never do

Writes `memory/notes/mine-{kind}-{hash}.md` with `source: script:raw_mine` and `raw_pointer`. Cursor: `state/raw-mine-cursor.json`.

## Evidence

```bash
cd "/home/mitun/anyonecancode development/.worktrees/feature-park-raw-mine"
python3 -m pytest plugins/anyone-can-code/tests/test_raw_capture_mine.py -q
python3 -m pytest plugins/anyone-can-code/tests/test_memory_promote.py plugins/anyone-can-code/tests/test_save_session.py plugins/anyone-can-code/tests/test_wiki_memory.py -q
python3 -m json.tool plugins/anyone-can-code/hooks/hooks.json >/dev/null
# still 10 hook events
python3 -c "import json; h=json.load(open('plugins/anyone-can-code/hooks/hooks.json')); print(sorted(h['hooks'])); print(len(h['hooks']))"
```

Expected: focused raw tests pass; promote/save/wiki still pass; **10** hook keys (unchanged).

## Hard locks check

- [x] ADD only — notes/wiki/learn/two drawers untouched as product surface
- [x] No full chat into SessionStart
- [x] Scripts mine (not model homework)
- [x] Secrets redacted before raw write
- [x] 10 hooks kept
- [x] No push/merge in this lane
