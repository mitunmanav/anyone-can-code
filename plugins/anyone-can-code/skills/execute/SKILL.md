---
name: execute
description: "Builds from the current task queue, follows the chosen route, and updates local workflow state without pretending unverified work is finished."
---

# Execute

Reply rule:

- talk strict caveman only
- keep answer short

Use `$execute` when the work is planned or concrete enough to implement.

## Inputs

- `.codex/anyone-can-code/artifacts/PLAN.md`
- `.codex/anyone-can-code/state/task-queue.md`
- relevant repo files

- tool_interop execute bindings: use installed skill; ACC redirect only; PRECHECK fail → local ACC + reason.

## Rules

- Extend existing code instead of rebuilding blindly.
- Keep route changes visible.
- Do not claim success until `$verify` or equivalent evidence exists.
- Update workflow state after meaningful progress.
- Update through `scripts/canonical_state.py`; derived files are not separate
  writable truths.
- Claim active tasks through `scripts/task_coordination.py` before execution.
  Do not start a task already claimed by another active owner.
- Complete tasks through the same coordinator with concise evidence.
- Loop-driven work (tdd loop, polish loop) has a loop_budget. After loop_budget iterations: STOP. Show real-use proof or ask user. Real-use proof = ran the actual product path, not unit tests alone. Do not keep looping past budget without user say-so.
- Before risky local work, remote work, external sharing, deletion, migration,
  install, publish, or release, use `scripts/safety_receipts.py` to write a
  receipt and verify approval, rollback, sandbox context, and remote authority.
- If `patch_retry` is present and a failed patch or stale edit target occurs,
  reread the exact target before retrying the failed patch. Stop and replan
  after the retry limit instead of repeating misses.
- If `mechanics_docs_gate` marks platform mechanics work, do not edit code
  until the docs brief exists. If official docs/source are missing, controlled
  proof must record uncertainty before platform mechanics code changes.
- Use only: `in scope`, `designed`, `approved`, `implemented`, `verified`,
  `blocked`, `deferred`.
- Code written but not checked is `implemented`, never `verified`.
- Record route, next step, evidence, failures, silent failures, unverified work,
  and uncertainty in workflow state.
- A mid-work requirement change updates route and next step before execution
  resumes.
- Scope change preserves old state in history, marks affected verification
  stale, updates every derived view, and moves active cursor to new work.
- Use subagents only when the user explicitly asked and Codex needs isolated
  or parallel work. Subagent output is bounded evidence, then control returns
  to ACC.
- Plain words only. No jargon (no "RLS", "monkeypatch", "tenant isolation" — say the plain thing).
- Warm, not a robot. Short is fine; cold is not. Never bark a one-word "Decide:" demand — offer the choice in a friendly line.

## Narration / walkthrough (always on)

- Narrate each build step as a robot walkthrough in plain lines — "Making the login page now." then "Done." then "Next: …"
- One short line per step. No code shown, no file paths, no jargon unless user asks.
- Step fails: one plain line — what broke + what you try next. Never hide it.
- Long multi-step work: offer native `/goal` so user can walk away (pause/resume). Works on CLI and Desktop.

## Output

- code changes
- updated workflow state
- optional notes under `.codex/anyone-can-code/artifacts/`

## Evidence rules

- Do not hardcode test counts in docs. Say "all tests green" and let CI show the number.
  Bad: "183 tests pass." Good: "all tests green."

## Worktree for risky work

Big refactor, experiment, or change that could break the working app: tell
the user in plain words — "Start this thread in Worktree mode: Codex works on
a safe copy, your real project stays untouched. When it is good, Handoff
moves it back." Git repositories only; no Git -> say so and proceed local
with extra care.
