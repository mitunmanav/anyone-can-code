# Proof — park lane: `$council` skill

Branch: `feature/park-council`  
Worktree: `.worktrees/feature-park-council`  
Date: 2026-08-03

## Codex docs first (required)

Ran before build:

```bash
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" skills
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" subagents
```

Also pulled chunked docs for:

- Build skills (`/codex/skills`) — SKILL.md + `name`/`description`; `agents/openai.yaml` for UI + `allow_implicit_invocation`; progressive disclosure / 8k list budget
- Subagents (`/codex/concepts/subagents`) — spawn when skill says so; parallel read-heavy; return summaries to main

Re-read after write: same topics (skills + subagents).

## What landed

| Path | Role |
|------|------|
| `plugins/anyone-can-code/skills/council/SKILL.md` | Multi-view read-only check (correctness / safety / honesty); caveman card; **not a ship gate — still run $verify** |
| `plugins/anyone-can-code/skills/council/agents/openai.yaml` | display_name `ACC council`; `allow_implicit_invocation: false` |
| `skills/orchestrator/SKILL.md` | Light route note: optional `$council`; keep `$bridge`; still `$verify` |
| `plugins/anyone-can-code/README.md` | Optional skills table row |
| `tests/test_skill_display_names.py` | EXPECTED map + council |
| `tests/test_skill_discovery.py` | EXPLICIT_ONLY includes council |

## Laws held

- Council **inside ACC** (not external Council product)
- `$bridge` stays
- Does **not** replace `$verify`
- No push / no merge
- Hooks untouched (still 10)

## How to check

```bash
# files
test -f plugins/anyone-can-code/skills/council/SKILL.md
test -f plugins/anyone-can-code/skills/council/agents/openai.yaml
rg -n 'not a ship gate' plugins/anyone-can-code/skills/council/SKILL.md
rg -n '\$council' plugins/anyone-can-code/skills/orchestrator/SKILL.md

# skill tests
python3 -m pytest plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py -q

# house budget + doctor slice
python3 plugins/anyone-can-code/scripts/doctor.py --json 2>/dev/null | head -c 2000
```

## PASS/FAIL

**PASS**

- `pytest` skill suite: **8 passed** (`test_skill_display_names`, `test_skill_discovery`, `test_skill_path_contract`, `test_skill_subagent_text`)
- Council body: **3106 chars** (under 4000 house budget)
- Hook events still **10** (SessionStart … PostCompact); hooks.json untouched
- Docs re-read after write: skills + subagents
