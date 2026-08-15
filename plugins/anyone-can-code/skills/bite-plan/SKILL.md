---
name: bite-plan
description: "Use when a feature or PLAN.md needs 2-5 min micro steps with checkboxes before build. Not for high-level routing ($plan). Explicit only."
---

# Bite plan

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Use `$bite-plan` to break work into **one-action, 2–5 minute** checkbox steps.
Fights context rot: small checkable bites, finish one, then next.

## Docs (Codex)

Skills: `SKILL.md` + optional `agents/openai.yaml` (`display_name`, `allow_implicit_invocation`).
Progressive disclosure: short description; full steps load on use.
Explicit `$bite-plan` only — no auto fire.

## Artifact

`.codex/anyone-can-code/artifacts/BITE_PLAN.md`

## Steps

1. **Inputs:** goal, SPEC-DRAFT, or existing PLAN.md.
2. **Decompose** into single actions (2–5 min each). Prefer TDD slices:
   - Write failing test
   - Run — expect fail
   - Minimal code
   - Run — expect pass
   - Commit (if user wants)
3. **Write file:**
   ```bash
   python3 "<ACC_PLUGIN_ROOT>/scripts/bite_plan.py" --repo . --write \
     --goal "…" --step "…" --step "…" --json
   ```
4. **Show** step count + first open step. Wait for **GO** before product writes.
5. **While building:** one step at a time. After verify:
   ```bash
   python3 "<ACC_PLUGIN_ROOT>/scripts/bite_plan.py" --repo . --mark N --json
   ```
6. **Check status:**
   ```bash
   python3 "<ACC_PLUGIN_ROOT>/scripts/bite_plan.py" --repo . --json
   ```

## Rules

- Each step = **one** action, not a whole feature.
- Minutes **clamp 2–5**. No 20-min "implement everything".
- Checkbox only after proof for that step.
- Differs from `$plan`: `$plan` = route + task queue; `$bite-plan` = micro execute list.
- No "done" without checks. No product write before GO when gate on.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "One big step is fine" | Split to 2–5 min bites. |
| "I'll track in chat" | Write BITE_PLAN.md. |
| "Skip verify mid-step" | Mark only after proof. |

## Next skill

- Need high-level tasks → `$plan` first
- User said GO → `$execute` using open bite steps
- Claiming done → `$verify`

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
