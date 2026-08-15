# Proof — plan-gate (feature/dr-plan-gate)

Branch: `feature/dr-plan-gate`  
Date: 2026-08-03  
Author: Mitun only  
NO PUSH. NO MERGE.

## Codex topics read (required)

Via `python3 codex\ docs/read-docs.py skills` and `hooks` + JSONL extract:

| Topic | URL / source | Used for |
|-------|----------------|----------|
| Build skills | https://developers.openai.com/codex/skills | SKILL.md frontmatter, progressive disclosure, `agents/openai.yaml` `display_name` / `allow_implicit_invocation` |
| Skills & plugins | https://developers.openai.com/codex/skills-and-plugins | Skill vs plugin packaging |
| Customization / skills concept | https://developers.openai.com/codex/concepts/customization | Skill folder shape (SKILL.md + scripts/references) |
| Hooks overview | https://developers.openai.com/codex/hooks | PreToolUse matchers, soft `additionalContext` vs hard `permissionDecision: deny` |
| PreToolUse | hooks docs (chunk PreToolUse) | `apply_patch` matcher aliases Edit/Write; soft hint shape only |
| Matcher patterns | hooks docs | `Bash\|apply_patch` already on ACC PreToolUse — no new hook event |

Re-read after write: same topics (skills metadata + PreToolUse soft context).

## What shipped

1. **Helper** `plugins/anyone-can-code/scripts/plan_gate.py`
   - `assess_plan` → `ok | missing | empty | no_steps | stale`
   - `extract_steps`, `is_product_write`, `pretool_soft_hint`, `write_plan_skeleton`
   - CLI: `python3 plan_gate.py --repo . --json`
2. **Skill** `$plan-gate` → display_name **ACC plan gate**
   - Path: `skills/plan-gate/SKILL.md` + `agents/openai.yaml`
3. **Plan skill** notes PLAN.md list steps required for gate
4. **Optional soft hook** in `guard.py` when `preferences.plan_gate_required` is true
   - Soft `additionalContext` only — **never hard deny** for plan missing
   - Default pref: `plan_gate_required: false` (skill-first)
5. **Tests** `test_plan_gate.py` + guard soft-hint cases + display name map

## Hooks count

Still **10** events in `hooks/hooks.json`. No `hooks: {}`. No new event type.

## Prove commands

```bash
cd "/home/mitun/anyonecancode development/.worktrees/feature-dr-plan-gate"
python3 -m pytest plugins/anyone-can-code/tests/test_plan_gate.py plugins/anyone-can-code/tests/test_skill_display_names.py plugins/anyone-can-code/tests/test_skill_discovery.py plugins/anyone-can-code/tests/test_guard.py -q
python3 plugins/anyone-can-code/scripts/plan_gate.py --repo . --json || true
python3 -m json.tool plugins/anyone-can-code/.codex-plugin/plugin.json >/dev/null
```

## Result

**PASS**

| Check | Result |
|-------|--------|
| `test_plan_gate.py` + display/discovery + guard | **37 passed** |
| `test_skill_path_contract.py` | **1 passed** |
| Hooks count | **10** (unchanged) |
| `plan_gate.py --json` on bare repo | `status=missing` exit 1 (expected) |
| Hard deny for missing plan | **No** (soft hint opt-in only) |

## Files

- `plugins/anyone-can-code/scripts/plan_gate.py`
- `plugins/anyone-can-code/skills/plan-gate/SKILL.md`
- `plugins/anyone-can-code/skills/plan-gate/agents/openai.yaml`
- `plugins/anyone-can-code/skills/plan/SKILL.md` (PLAN.md steps note)
- `plugins/anyone-can-code/hooks/scripts/guard.py` (soft hint)
- `plugins/anyone-can-code/hooks/scripts/state.py` (`plan_gate_required` default false)
- `plugins/anyone-can-code/tests/test_plan_gate.py`
- `plugins/anyone-can-code/tests/test_guard.py` (2 soft-hint cases)
- `plugins/anyone-can-code/tests/test_skill_display_names.py`
- `plugins/anyone-can-code/tests/test_skill_discovery.py`
- `docs/proof/dr-plan-gate.md`
