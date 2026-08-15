# Proof: progress ledger / fight context rot

**Branch:** `feature/dr-context-rot`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** local worktree only — no push, no merge

## Docs first (Codex)

Commands run:

```bash
python3 "codex docs/read-docs.py" hooks
python3 "codex docs/read-docs.py" skills
python3 "codex docs/read-docs.py" --show hooks   # SessionStart / PreCompact
```

Relevant facts used:

| Event | Inject field | Notes |
| --- | --- | --- |
| `SessionStart` | `hookSpecificOutput.additionalContext` | developer context; sources `startup\|resume\|clear\|compact` |
| `PreCompact` / `PostCompact` | common `systemMessage` | PostCompact does **not** document `additionalContext` |
| `Stop` | JSON only; no non-JSON stdout | save stays silent `{}` on success |

Skill packaging: plugin skills under `plugins/anyone-can-code/skills/<name>/SKILL.md` + `agents/openai.yaml`.

## What shipped

1. **`plugins/anyone-can-code/scripts/context_rot.py`**
   - Disk: `.codex/anyone-can-code/state/progress-ledger.md`
   - Sections: WHERE / NEXT / DONE / OPEN (+ NOTES for capsule pointers)
   - API: `init`, `set_where`, `set_next`, `append_done`, `append_open`, `append_capsule_pointer`, `render`, `inject_line`, `sync_from_workflow`, CLI
   - Caps: `INJECT_MAX_CHARS=320`, `MAX_DONE_KEEP=12`, `MAX_OPEN_KEEP=12`

2. **Skill `$ledger`** (`skills/ledger/`) — optional progressive skill for init/update/show

3. **`load_session.py`** — thin one-liner inject **only if ledger file exists**; opt-out via prefs `progress_ledger_inject=false`. Does not create ledger.

4. **`compact.py` PreCompact** — if ledger exists, NOTES pointer → `state/compact-capsule.md`

5. **`save_session.py` Stop** — if ledger exists: sync WHERE/NEXT from workflow, NOTES pointer → `state/session-snapshot.md`, light DONE from summary. No auto-create.

6. **Hooks count:** still 10 (no hooks.json shape change).

## Tests

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_context_rot.py -q
```

Expected: **11 passed** (round-trip, inject cap, load_session present/absent, save capsule pointer, DONE cap).

Related smoke (optional):

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_load_session.py plugins/anyone-can-code/tests/test_save_session.py plugins/anyone-can-code/tests/test_compact.py plugins/anyone-can-code/tests/test_skill_path_contract.py -q
```

## Manual check

```bash
python3 plugins/anyone-can-code/scripts/context_rot.py --project /tmp/acc-ledger-demo init --where "demo" --next "prove inject"
python3 plugins/anyone-can-code/scripts/context_rot.py --project /tmp/acc-ledger-demo done "init ok"
python3 plugins/anyone-can-code/scripts/context_rot.py --project /tmp/acc-ledger-demo inject
# → Ledger: WHERE=demo | NEXT=prove inject | done=1 open=0 | file=.codex/anyone-can-code/state/progress-ledger.md
```

## Non-goals (this branch)

- No force-continue hooks
- No new hook event
- No merge/push
- Does not replace workflow.json / portable handoff / PROGRESS.md — adds a small board for multi-step anti-rot
