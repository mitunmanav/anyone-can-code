# Proof: feature/dr-parallel-fix

**Branch:** `feature/dr-parallel-fix`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** multi-agent fan-out when many pytest files fail  
**Push/merge:** none

## Docs first

- Codex **Build skills**: `SKILL.md` + optional `agents/openai.yaml` (`display_name`, `allow_implicit_invocation`).
- Codex **Subagents**: parallel specialized agents; skill may request fan-out; careful with parallel writes → **one file per subagent**.

## Delivered

| Item | Path |
|------|------|
| Skill | `plugins/anyone-can-code/skills/parallel-fix/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/parallel-fix/agents/openai.yaml` |
| Parser | `plugins/anyone-can-code/scripts/parallel_fix.py` |
| Tests | `plugins/anyone-can-code/tests/test_parallel_fix.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC parallel fix"` |
| Explicit-only | `tests/test_skill_discovery.py` → `parallel-fix` in `EXPLICIT_ONLY` |

## Behavior

1. Parse pytest log → unique failed **files** (order stable).
2. 0 → stop; 1 → serial `$fix`; 2+ → one read-write subagent per file.
3. Wait all → full suite re-run → report card.
4. `allow_implicit_invocation: false` (explicit `$parallel-fix` only).

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_parallel_fix.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py -q
# 12 passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 588 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` = **2101** chars (limit 4000).

## How to re-check

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_parallel_fix.py -q
python3 plugins/anyone-can-code/scripts/parallel_fix.py --json <<'EOF'
FAILED tests/a.py::t - x
ERROR tests/b.py::t - y
EOF
# → ["tests/a.py", "tests/b.py"]
```

## PASS/FAIL

**PASS** — parser + skill registration + full suite green. No push. No merge.
