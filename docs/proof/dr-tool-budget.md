# Proof: feature/dr-tool-budget

**Branch:** `feature/dr-tool-budget`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** Cascade-style soft tool-call budget + `$tool-budget`  
**Push/merge:** none

## Docs first (Codex)

- Build skills: https://developers.openai.com/codex/skills  
  (`SKILL.md` + optional `agents/openai.yaml` display_name / policy)
- Hooks: https://developers.openai.com/codex/hooks  
  (PostToolUse `additionalContext` soft inject; keep event count = 10)
- Local index: `python3 ".../codex docs/read-docs.py" skills` and `hooks`

## WEB (Windsurf / Cascade)

- Cascade overview (tool call limit + continue + Auto-Continue):  
  https://docs.devin.ai/desktop/cascade  
  Quote: *Cascade can make up to 20 tool calls per prompt. If the trajectory stops, simply press the continue button… Auto-Continue setting…*
- Full docs dump (Auto-Continue note):  
  https://docs.windsurf.com/llms-full.txt  
- Usage / credits context (not the same as tool count):  
  https://docs.devin.ai/desktop/accounts/usage

## Delivered

| Item | Path |
|------|------|
| Counter script | `plugins/anyone-can-code/scripts/tool_budget.py` |
| State file | `.codex/anyone-can-code/state/tool-budget.json` (runtime) |
| Skill | `plugins/anyone-can-code/skills/tool-budget/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/tool-budget/agents/openai.yaml` |
| Soft PostToolUse | `plugins/anyone-can-code/hooks/scripts/audit.py` (clean only; prefs `tool_budget_track`) |
| Tests | `plugins/anyone-can-code/tests/test_tool_budget.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC tool budget"` |
| Explicit-only | `tests/test_skill_discovery.py` → `tool-budget` in `EXPLICIT_ONLY` |

## Behavior

1. Default limit **20** (Cascade parity). Soft warn at 80%; **over** at limit.
2. Soft only — never hard deny / never new hook event (still **10** hooks).
3. `continue` → new segment, count 0 (Cascade continue button idea).
4. Optional clean PostToolUse increment when `tool_budget_track` not false (default on).
5. `$tool-budget` explicit only (`allow_implicit_invocation: false`).

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_tool_budget.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py \
  plugins/anyone-can-code/tests/test_token_budget.py \
  plugins/anyone-can-code/tests/test_locked_guards.py -q
# 21 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 589 passed, 2 skipped, 122 subtests passed
```

Skill body: **~1811** chars (limit 4000).

## How to re-check

```bash
python3 plugins/anyone-can-code/scripts/tool_budget.py --project . init --limit 20
python3 plugins/anyone-can-code/scripts/tool_budget.py --project . status
python3 plugins/anyone-can-code/scripts/tool_budget.py --project . continue
python3 -m pytest plugins/anyone-can-code/tests/test_tool_budget.py -q
```

## PASS/FAIL

**PASS** — counter + soft warn + skill registration + full suite green. No push. No merge.
