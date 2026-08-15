# Proof: feature/dr-cost-guard

**Branch:** `feature/dr-cost-guard`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** soft tips for cheap vs strong Codex models (Luna / Terra / Sol)  
**Push/merge:** none

## Docs first

- Codex **Build skills**: `SKILL.md` + `agents/openai.yaml` (`display_name`, `allow_implicit_invocation`).
- Codex **Models**: user chooses Sol / Terra / Luna + reasoning; Desktop UI, CLI `/model` / `-m`, `config.toml`.
- Local: `python3 "…/codex docs/read-docs.py" skills|models|usage`.

## WEB (pricing + models)

| Source | URL |
|--------|-----|
| API pricing (post 2026-07-30) | https://developers.openai.com/api/docs/pricing |
| GPT-5.6 announcement | https://openai.com/index/gpt-5-6/ |
| Luna −80% / Terra −20% cut | https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/ |
| Codex models guide | https://developers.openai.com/codex/models |
| Codex pricing / credits | https://developers.openai.com/codex/pricing |

### API short-context snapshot (helper `as_of` 2026-08-03)

| Tier | Model id | Input / 1M | Output / 1M |
|------|----------|------------|-------------|
| Luna | `gpt-5.6-luna` | $0.20 | $1.20 |
| Terra | `gpt-5.6-terra` | $2.00 | $12.00 |
| Sol | `gpt-5.6-sol` | $5.00 | $30.00 |

## Delivered

| Item | Path |
|------|------|
| Skill | `plugins/anyone-can-code/skills/cost-guard/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/cost-guard/agents/openai.yaml` |
| Helper | `plugins/anyone-can-code/scripts/cost_guard.py` |
| Tests | `plugins/anyone-can-code/tests/test_cost_guard.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC cost guard"` |
| Explicit-only | `tests/test_skill_discovery.py` → `cost-guard` in `EXPLICIT_ONLY` |

## Behavior

1. Classify task keywords → Luna / Terra / Sol (default Terra).
2. Emit soft tip + price snapshot + honesty line.
3. **Honesty:** ACC cannot force Codex model picker.
4. `allow_implicit_invocation: false` (explicit `$cost-guard` only).
5. No hooks change. Keep 10 hooks.

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_cost_guard.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py -q
# 17 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 593 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` = **2071** chars (limit 4000).

## How to re-check

```bash
python3 plugins/anyone-can-code/scripts/cost_guard.py --json rename and lint
# → tier luna, honesty present

python3 plugins/anyone-can-code/scripts/cost_guard.py --catalog
python3 -m pytest plugins/anyone-can-code/tests/test_cost_guard.py -q
```

## PASS/FAIL

**PASS** — helper + skill registration + full suite green. No push. No merge.
