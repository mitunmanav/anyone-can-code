# Proof: feature/dr-repo-map

**Branch:** `feature/dr-repo-map`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** pure-Python ranked repo map sample + optional SessionStart inject  
**Push/merge:** none

## Docs first (WEB)

| Source | URL |
|--------|-----|
| Aider repository map | https://aider.chat/docs/repomap.html |
| Aider tree-sitter map blog | https://aider.chat/2023/10/22/repomap.html |
| Codex Build skills (`allow_implicit_invocation`) | https://learn.chatgpt.com/docs/build-skills |
| Superpowers (TDD + verify-before-done) | https://github.com/obra/superpowers |

### Steal pattern (not copy)

Aider: files + key symbols; graph rank; fit budget.  
ACC: **stdlib only**, regex defs + reference-frequency rank, write sample to disk, **thin inject only if file exists**.

## Superpowers

1. Tests first (`test_repo_map.py`)  
2. Minimal code green  
3. Verify suite before claim done  

## Delivered

| Item | Path |
|------|------|
| Script | `plugins/anyone-can-code/scripts/repo_map.py` |
| Skill | `plugins/anyone-can-code/skills/repo-map/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/repo-map/agents/openai.yaml` |
| SessionStart | `plugins/anyone-can-code/hooks/scripts/load_session.py` (Tier B, if file + cap) |
| Tests | `plugins/anyone-can-code/tests/test_repo_map.py` |
| EXPECTED | `"repo-map": "ACC repo map"` |
| Explicit-only | `EXPLICIT_ONLY` includes `repo-map` |

## Behavior

1. **build** → `.codex/anyone-can-code/artifacts/repo-map.md` (ranked paths + symbols).  
2. Rank = definition extract + cross-file name frequency + small entry/depth bonuses.  
3. Skips junk (`node_modules`, `.git`, venvs, caches, …).  
4. SessionStart: inject **only if artifact exists**, hard cap `INJECT_MAX_CHARS=600`.  
5. Prefs opt-out: `repo_map_inject=false`.  
6. Skill explicit-only (`allow_implicit_invocation: false`).  
7. No AI. No network. No tree-sitter dep.

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_repo_map.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py -q
# 16 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 592 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` ≤ 4000 chars.

## How to re-check

```bash
python3 plugins/anyone-can-code/scripts/repo_map.py --project . build
python3 plugins/anyone-can-code/scripts/repo_map.py --project . inject
python3 plugins/anyone-can-code/scripts/repo_map.py --project . rank --json | head
python3 -m pytest plugins/anyone-can-code/tests/test_repo_map.py -q
```

## Non-goals

- No tree-sitter / ctags install  
- No auto-build on every SessionStart  
- No push / no merge  
- Not a full code graph (codegraph remains separate)

## PASS/FAIL

**PASS** — unit + skill registration + full suite green. No push. No merge.
