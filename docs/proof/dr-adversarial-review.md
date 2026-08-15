# Proof — feature/dr-adversarial-review

**Date:** 2026-08-03  
**Worktree:** `.worktrees/feature-dr-adversarial-review`  
**Branch:** `feature/dr-adversarial-review`  
**Constraint:** No push. No merge. Mitun only. Keep 10 hooks.

---

## What shipped

| Piece | Path |
|-------|------|
| Skill | `plugins/anyone-can-code/skills/skeptic/SKILL.md` (`$skeptic`) |
| UI / policy | `skills/skeptic/agents/openai.yaml` — display **ACC skeptic**, explicit-only |
| Helper | `plugins/anyone-can-code/scripts/skeptic.py` — list changed files (mockable) |
| Tests | `plugins/anyone-can-code/tests/test_skeptic.py` + EXPECTED/EXPLICIT/RUNTIME registration |
| README | optional skills table row |
| Orchestrator | one-line optional `$skeptic` (not `$verify`) |

---

## Behavior (product)

1. **Read-only** review of git working tree / `--base` diff / named files.
2. Three views: correctness, safety, honesty/omissions.
3. **Does not replace `$verify`** — ship gate still verify.
4. Write `.codex/anyone-can-code/artifacts/SKEPTIC.md` **only if user asks** save.
5. Explicit invocation only (`allow_implicit_invocation: false`).

---

## PASS / FAIL

| Check | Result |
|-------|--------|
| Codex skills docs: SKILL.md + agents/openai.yaml | **PASS** |
| TDD tests for helper + skill contract | **PASS** |
| Named paths win without git | **PASS** |
| Mocked `git status` / `git diff --name-only` | **PASS** |
| Explicit-only + display_name ACC skeptic | **PASS** |
| Not a `$verify` substitute (skill text) | **PASS** |
| Save opt-in only | **PASS** |
| Skill ≤ 4000 chars | **PASS** |
| Hooks still 10 events | **PASS** |
| No push / no merge | **PASS** |

### Commands

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_skeptic.py -q
python3 -m pytest plugins/anyone-can-code/tests -q
python3 plugins/anyone-can-code/scripts/skeptic.py --list-changed --json
python3 plugins/anyone-can-code/scripts/skeptic.py --list-changed -- path/a.py
```

---

## Docs first

- Skills: `allow_implicit_invocation`, progressive load, `display_name` in `agents/openai.yaml`.
- Code review host tools stay host-side; ACC `$skeptic` is plugin skill (read-only second pass).

---

## Out of scope (this lane)

- Auto-force prove-done via Stop hooks
- Replacing `$verify` or security_gate
- Push / merge / release
