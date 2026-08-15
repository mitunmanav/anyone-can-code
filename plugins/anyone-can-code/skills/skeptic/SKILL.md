---
name: skeptic
description: "Use when user asks $skeptic / adversarial review / second pass on a diff. Read-only. Not a substitute for $verify."
---

# Skeptic

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject). PLUGIN_ROOT is hooks-only.

Talk strict caveman. Short.

Use `$skeptic` for a **read-only** adversarial second pass on a git diff or named files.

## Hard rules

- **Read-only.** Do not edit product files. No tree writes. No "fix while reviewing."
- **Does not replace `$verify`.** Ship gate still `$verify` with real evidence.
- Save to `.codex/anyone-can-code/artifacts/SKEPTIC.md` **only if user asks** save.

## Scope

1. Named files from user → use those.
2. Else run:
   `python3 "<ACC_PLUGIN_ROOT>/scripts/skeptic.py" --list-changed`
   Optional base: `--base main` (or other ref).
3. Read those files + `git diff` (or named content). No silent expand of scope.

## Review views (all three)

| View | Look for |
|------|----------|
| **Correctness** | Logic bugs, edge misses, broken contracts, tests lying |
| **Safety** | Secrets, shell injection, path escape, unsafe defaults, data loss |
| **Honesty / omissions** | Claims without evidence, missing limits, silent scope creep, docs vs code |

## Output (chat)

Short report:

1. Scope (files)
2. Findings: severity · view · file · note
3. Verdict: blockers / risks / clean-enough
4. Next: `$verify` before done; `$fix` only if user wants changes

## Save (opt-in)

If user says save: write `.codex/anyone-can-code/artifacts/SKEPTIC.md` only.
Use helper shape from `scripts/skeptic.py` `format_skeptic_md` if useful.

## Done — back to normal

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again.
