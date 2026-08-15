# Proof: feature/dr-strong-oneshot

**Branch:** `feature/dr-strong-oneshot`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** strong one-shot mode — one focused goal → plan → TDD → verify → proof  
**Push/merge:** none

## Docs first

- Codex **Build skills**: `SKILL.md` + `agents/openai.yaml` (`display_name`, `allow_implicit_invocation`).
- Codex **Hooks**: unchanged (still **10** command hooks). Skill-only process; no new hook.
- Host long-horizon coding (GPT-5.x / Codex) = **model capability**. ACC adds **process discipline** only (checklist + force chain + no-done-without-verify).

## Delivered

| Item | Path |
|------|------|
| Skill | `plugins/anyone-can-code/skills/oneshot/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/oneshot/agents/openai.yaml` |
| Checklist | `plugins/anyone-can-code/scripts/oneshot_checklist.py` |
| Tests | `plugins/anyone-can-code/tests/test_oneshot_checklist.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC strong run"` |
| Explicit-only | `tests/test_skill_discovery.py` → `oneshot` in `EXPLICIT_ONLY` |

## Behavior

1. State machine: **plan → build → verify → done**. Skip → error.
2. `verify` requires non-empty **evidence** string (fresh command + result).
3. `ok_to_claim_done` only after verify evidence recorded this run.
4. Optional `ledger` subcommand writes thin `progress-ledger.md`.
5. `allow_implicit_invocation: false` (explicit `$oneshot` / strong-run only).
6. Status card for end of run.

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_oneshot_checklist.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py -q
# 18 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 594 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` = **2774** chars (limit 4000).  
Hooks: **10** command entries (unchanged).

## How to re-check

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_oneshot_checklist.py -q
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os init --goal "demo"
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os advance plan
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os advance build
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os advance verify --evidence "pytest -q → pass"
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os status --card
# skip must fail:
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os2 init --goal x
python3 plugins/anyone-can-code/scripts/oneshot_checklist.py --repo /tmp/os2 advance done; echo $?  # nonzero
```

## PASS/FAIL

**PASS** — checklist transitions + skill registration + full suite green. No push. No merge. Hooks stay 10.
