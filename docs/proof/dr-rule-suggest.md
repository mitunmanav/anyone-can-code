# PROOF — dr-rule-suggest

**Branch:** `feature/dr-rule-suggest`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**No push. No merge.**

## What

Cursor-style durable rule suggestions when the same fix/frustration repeats.

| Piece | Path |
|-------|------|
| Skill | `plugins/anyone-can-code/skills/rule-suggest/SKILL.md` |
| UI label | `skills/rule-suggest/agents/openai.yaml` → **ACC rule suggest** |
| Policy | `allow_implicit_invocation: false` (explicit-only) |
| Helper | `plugins/anyone-can-code/scripts/rule_suggest.py` |

## Behavior

1. Fingerprint notes under `.codex/anyone-can-code/memory/notes/` and
   `state/prompt-log.jsonl` (if present).
2. Patterns seen **3+** times → suggestion list (wiki/learn note text **or**
   `AGENTS.md` bullet).
3. **Suggest only.** Skill waits for user **YES** before any write.
4. Helper never writes files.

## Checks run

```bash
python3 -m pytest \
  plugins/anyone-can-code/tests/test_rule_suggest.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_ship_set.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py \
  -q
```

**Result:** 20 passed, 35 subtests passed.

Focused suite:

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_rule_suggest.py -q
```

**Result:** 8 passed (fingerprint, notes, prompt-log, no-write, yaml reg).

Skill budget: `SKILL.md` = 1742 chars (under doctor 4000).

CLI smoke:

```bash
python3 plugins/anyone-can-code/scripts/rule_suggest.py --help
# exits 0; describe: suggest only / no write
```

## Manual (user)

1. `$rule-suggest` in Codex after repeated same fix language.
2. Confirm list shows options A/B.
3. Say no → nothing written. Say yes → only chosen path.

## Not in this lane

- No auto-fire every turn
- No merge / push
- Does not replace hook `rule_promote` (permanent `memory/rules.md`)
