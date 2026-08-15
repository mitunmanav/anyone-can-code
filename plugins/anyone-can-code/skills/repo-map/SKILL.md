---
name: repo-map
description: "Use when user wants a ranked repo map sample (paths + key symbols), $repo-map, or Aider-style map without AI. Explicit only — not auto."
---

# Repo map

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$repo-map` to build a **small ranked map** of paths + key symbols. Pure Python rank. **No AI.** Not a full AST.

## Docs inspiration

- Aider repo map: https://aider.chat/docs/repomap.html
- Aider tree-sitter map writeup: https://aider.chat/2023/10/22/repomap.html

ACC version is **lighter**: regex symbols + reference frequency rank + size caps. No tree-sitter dep.

## File

`.codex/anyone-can-code/artifacts/repo-map.md`

## Commands

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/repo_map.py" --project "." build
python3 "<ACC_PLUGIN_ROOT>/scripts/repo_map.py" --project "." show
python3 "<ACC_PLUGIN_ROOT>/scripts/repo_map.py" --project "." inject
python3 "<ACC_PLUGIN_ROOT>/scripts/repo_map.py" --project "." rank --json
```

## Steps

1. Run **build** from project root.
2. Point user at the file (do not paste whole map unless tiny).
3. Optional: `rank --json` for tool use.
4. SessionStart injects a **thin cap** only if the file already exists (opt-out prefs `repo_map_inject=false`). Skill does **not** auto-build on start.

## Rules

- Explicit `$repo-map` only (`allow_implicit_invocation: false`).
- No network. No model ranking. Stdlib only.
- Caps: scan junk dirs skipped; map + inject hard char limits.
- Large monorepo: still a **sample** of top-ranked files — not complete truth.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
