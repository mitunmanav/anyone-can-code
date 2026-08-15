# Proof: session resume card (LAST handoff + progress-ledger)

**Branch:** `feature/dr-session-resume`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** local worktree only — no push, no merge

## Docs first (WEB + Codex)

### Claude Code sessions

| Source | Fact used |
| --- | --- |
| [Manage sessions](https://code.claude.com/docs/en/sessions) | `claude --continue` = most recent session in cwd; `--resume` / `/resume` = picker; `/compact` summarizes history |
| Same | Resume can offer **resume from summary** after long idle + large transcript — disk/handoff still needed for work truth |
| [Hooks](https://code.claude.com/docs/en/hooks) | SessionStart re-runs on resume (`source=resume`) and can refresh context |

### Superpowers / durable progress

| Source | Fact used |
| --- | --- |
| Superpowers SDD progress ledger (`.superpowers/sdd/progress.md` pattern) | Durable board survives reset; trust file + git over chat memory |
| Superpowers plan checkboxes | Task marks = session recovery map after death/compact |
| Handoff-resume pattern | Load latest unrestored handoff → short summary → continue from Next |

### Codex hooks / SessionStart

Commands (when local docs available):

```bash
python3 "codex docs/read-docs.py" hooks
python3 "codex docs/read-docs.py" --show hooks
```

| Event | Field | Notes |
| --- | --- | --- |
| `SessionStart` | `source` | `startup` \| `resume` \| `clear` \| `compact` |
| `SessionStart` | `additionalContext` / plain stdout | inject developer context; keep small |
| After compact | `source=compact` | re-anchor before next model request |
| ACC matcher | `hooks.json` | already `startup\|resume\|clear\|compact` — **no new hook** |

Native resume remains host-owned: `codex resume` / `--last`, `codex exec resume`, app-server `thread/resume`. ACC owns **work truth** files only.

## What shipped

1. **`plugins/anyone-can-code/scripts/session_resume.py`**
   - Reads (no create):
     - LAST handoff: `.codex/anyone-can-code/artifacts/PORTABLE_HANDOFF.md`
     - Progress ledger if present: `.codex/anyone-can-code/state/progress-ledger.md`
   - Prints short **Resume card**: WHERE / NEXT / DONE / OPEN (capped) + HANDOFF/LEDGER status + Native line
   - Ledger WHERE/NEXT win when set; else handoff Goal / Next step
   - Secret redaction + `CARD_MAX_CHARS=900`

2. **`$resume` skill** (`skills/resume/SKILL.md`)
   - **Step 0:** always run `session_resume.py --project .` before recovery modes
   - Points at handoff + progress-ledger paths
   - Notes SessionStart sources / compact re-anchor

3. **Hooks count:** still 10 (no `hooks.json` change).

## Tests

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_session_resume.py -q
```

Expected: **PASS** (empty / handoff / ledger / both / caps / redaction / CLI / skill step0).

## Manual check

```bash
# empty
python3 plugins/anyone-can-code/scripts/session_resume.py --project /tmp/acc-resume-empty

# with handoff
mkdir -p /tmp/acc-resume-demo/.codex/anyone-can-code/artifacts
cp path/to/PORTABLE_HANDOFF.md /tmp/acc-resume-demo/.codex/anyone-can-code/artifacts/
python3 plugins/anyone-can-code/scripts/session_resume.py --project /tmp/acc-resume-demo
```

## Non-goals

- No push / merge
- No new hook event
- Does not auto-create progress-ledger (that is `$ledger` / `context_rot` on other branch)
- Does not replace native Codex resume or full `$status`
