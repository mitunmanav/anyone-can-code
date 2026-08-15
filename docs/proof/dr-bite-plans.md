# Proof: feature/dr-bite-plans

**Branch:** `feature/dr-bite-plans`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** `$bite-plan` — 2–5 min checkbox micro-steps → `artifacts/BITE_PLAN.md`  
**Push/merge:** none

## Docs first (WEB + local)

| Topic | URL / source | Used for |
|-------|----------------|----------|
| Superpowers writing-plans | https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md | Bite-sized 2–5 min steps; checkbox `- [ ]`; TDD slices |
| Superpowers writing-plans (overview) | https://mridullpandey-superpowers.mintlify.app/workflow/writing-plans | Over-specified micro tasks + verify |
| GSD / context rot | https://github.com/gsd-build/get-shit-done | Small checkable plans; fresh focus per unit |
| GSD context rot explain | https://thenewstack.io/beating-the-rot-and-getting-stuff-done/ | Task framework fights context rot |
| GSD medium | https://agentnativedev.medium.com/get-sh-t-done-meta-prompting-and-spec-driven-development-for-claude-code-and-codex-d1cde082e103 | Stop one long thread; small plans |
| Codex Build skills | https://developers.openai.com/codex/skills | `SKILL.md` + `agents/openai.yaml` `display_name` / `allow_implicit_invocation` |
| Skills & plugins | https://developers.openai.com/codex/skills-and-plugins | Skill packaging |
| Local chunker | `codex docs/read-docs.py skills` | Re-read skills metadata after write |

## Delivered

| Item | Path |
|------|------|
| Skill | `plugins/anyone-can-code/skills/bite-plan/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/bite-plan/agents/openai.yaml` |
| Helper | `plugins/anyone-can-code/scripts/bite_plan.py` |
| Tests | `plugins/anyone-can-code/tests/test_bite_plan.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC bite plan"` |
| Explicit-only | `tests/test_skill_discovery.py` → `bite-plan` in `EXPLICIT_ONLY` |
| Path contract | `BITE_PLAN.md` in `RUNTIME_FILES` |

## Behavior

1. Format steps as checkbox markdown (`- [ ] **N.** text (~M min)`).
2. Minutes clamp **2–5** (default 3).
3. Write/read `.codex/anyone-can-code/artifacts/BITE_PLAN.md`.
4. Assess: `ok | missing | empty | no_steps`.
5. `--mark N` toggles step done after verify.
6. `allow_implicit_invocation: false` (explicit `$bite-plan` only).

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_bite_plan.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py -q
# 18 passed
```

## How to re-check

```bash
cd "/home/mitun/anyonecancode development/.worktrees/feature-dr-bite-plans"
python3 -m pytest plugins/anyone-can-code/tests/test_bite_plan.py -q
python3 plugins/anyone-can-code/scripts/bite_plan.py --repo . --write \
  --goal "Demo" --step "Write failing test" --step "Implement" --json
python3 plugins/anyone-can-code/scripts/bite_plan.py --repo . --mark 1 --json
```

## PASS/FAIL

**PASS** — formatter + skill registration + path contract green. No push. No merge.
