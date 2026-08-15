# Proof: feature/dr-auto-lint

**Branch:** `feature/dr-auto-lint`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** Aider-style after-edit lint/test detect + soft PostToolUse hint  
**Push/merge:** none

## Docs first (web + Codex topics)

| Source | URL / topic | Takeaway |
|--------|-------------|----------|
| Aider lint/test | https://aider.chat/docs/usage/lint-test.html | Auto-lint after edits; optional auto-test; feed failures back to model |
| Aider options | https://aider.chat/docs/config/options.html | `--auto-lint` / `--auto-test` / `--lint-cmd` / `--test-cmd` |
| Codex Hooks | https://learn.chatgpt.com/docs/hooks | `PostToolUse` → command hook; `additionalContext` soft inject (not undo) |
| Superpowers TDD | https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md | RED → green → verify before done |

**Codex topics used:** PostToolUse, `hookSpecificOutput.additionalContext`, PermissionRequest fail-closed stays separate, skills `agents/openai.yaml` (`display_name`, `allow_implicit_invocation`).

## Delivered

| Item | Path |
|------|------|
| Detector | `plugins/anyone-can-code/scripts/auto_lint.py` |
| Soft hook | `plugins/anyone-can-code/hooks/scripts/audit.py` → `maybe_auto_lint_context` |
| Skill | `plugins/anyone-can-code/skills/auto-lint/SKILL.md` |
| UI / policy | `skills/auto-lint/agents/openai.yaml` → **ACC auto lint**, explicit-only |
| Tests | `plugins/anyone-can-code/tests/test_auto_lint.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"auto-lint": "ACC auto lint"` |
| Explicit-only | `tests/test_skill_discovery.py` → `auto-lint` in `EXPLICIT_ONLY` |

## Behavior

1. **Detect** pytest / ruff / eslint only when layout or config present.
2. **Skill `$auto-lint`:** detect → run commands → report card. Explicit only.
3. **Pref `auto_lint: true`** in `.codex/anyone-can-code/settings/preferences.json`:
   - PostToolUse on **edit-like** tools only (`apply_patch`, `Write`, `Edit`, …)
   - Soft `additionalContext` listing commands + `$auto-lint`
   - Default **off**
4. **Never** deny / never fail-closed from auto-lint path. Strong failure / circuit breaker / silent-fail / exit-124 win first.
5. Exceptions inside auto-lint path swallowed → empty hint.

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_auto_lint.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_circuit_breaker.py -q
# 23 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 595 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` = **1909** chars (limit 4000).

CLI smoke:

```bash
python3 plugins/anyone-can-code/scripts/auto_lint.py --json --root .
# → [{"name":"pytest","kind":"test","command":"python -m pytest -q",...}]
```

## How to re-check

```bash
# focused
python3 -m pytest plugins/anyone-can-code/tests/test_auto_lint.py -q

# detect only
python3 plugins/anyone-can-code/scripts/auto_lint.py --json --root /path/to/proj

# soft hint text
python3 plugins/anyone-can-code/scripts/auto_lint.py --hint --root /path/to/proj
```

Manual (user): set `"auto_lint": true` in preferences → edit a file in Codex → model sees soft AUTO-LINT context. Or invoke `$auto-lint`.

## PASS/FAIL

**PASS** — detect + skill reg + soft opt-in PostToolUse + full suite green.  
No push. No merge.
