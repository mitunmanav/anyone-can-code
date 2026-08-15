---
name: oneshot
description: "Use when user wants one focused goal to done with proof (strong one-shot / $strong-run). Full chain: clarify? → plan → TDD build → verify → card. Not for multi-goal sprawl or pure chat."
---

# Strong run ($oneshot / $strong-run)

Script root: `ACC_PLUGIN_ROOT` from SessionStart (hooks inject).

Reply rule:

- talk strict caveman only
- keep answer short

Explicit only — do not auto-fire. Host model = long-horizon coding (GPT-5.x Codex).
ACC adds **process discipline** only (plan + TDD + verify + proof). Not a smarter model.

## Force chain (no skip)

1. **Clarify?** Only if goal fuzzy. One blocking ask max. Else skip.
2. **Plan** — write/update `.codex/anyone-can-code/artifacts/PLAN.md` with list steps.
3. **Build** — TDD execute (test first when code). Stay on **one** goal.
4. **Verify** — fresh `$verify` evidence **this turn** (command + output).
5. **Status card** — then stop. Back to normal chat.

## Checklist helper

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . init --goal "one focused goal"
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . advance plan --note "PLAN.md steps"
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . advance build --note "TDD"
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . advance verify --evidence "pytest … → N passed"
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . advance done
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . status --card
```

Skip a phase → script **errors**. That is the point.

Optional ledger:

```bash
python3 "<ACC_PLUGIN_ROOT>/scripts/oneshot_checklist.py" --repo . ledger --where "oneshot: <goal>" --next "<step>"
```

## HARD-GATE / iron law

**No "done", "works", "fixed", "shipped" without verify evidence this turn.**

Built ≠ verified. Old runs ≠ now. Diff ≠ proof.

## Red flags — stop

| Thought | Reality |
|---------|---------|
| "Too small for plan" | Tiny PLAN.md still. |
| "I'll verify later" | No. Verify before done. |
| "Tests passed earlier" | Fresh run this turn. |
| "Multi features while here" | One goal. Park the rest. |
| "Skip checklist, I know" | Run helper. Fail on skip. |

## Status card (end of run)

```
WHERE: oneshot / strong-run
GOAL: …
PHASE: done
COMPLETED: plan, build, verify, done
DONE?: YES
EVIDENCE: <command + result>
NEXT: stop or $learn
```

## Next skill

Inside chain: plan → execute (build) → verify. After card: optional `$learn`. Leftovers → new oneshot or `$plan`.

## Done — back to normal

When this skill's job is finished:

1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
