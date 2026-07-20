# Execute details (read when needed)

## Full rules

- Extend existing code instead of rebuilding blindly.
- Keep route changes visible.
- Do not claim success until `$verify` or equivalent evidence exists.
- Update workflow state after meaningful progress.
- Update through `scripts/canonical_state.py`; derived files are not separate
  writable truths.
- Claim active tasks through `scripts/task_coordination.py` before execution.
  Do not start a task already claimed by another active owner.
- Complete tasks through the same coordinator with concise evidence.
- Loop-driven work (tdd loop, polish loop) has a loop_budget. After loop_budget
  iterations: STOP. Show real-use proof or ask user. Real-use proof = ran the
  actual product path, not unit tests alone. Do not keep looping past budget
  without user say-so.
- Risky ship/delete/remote: `scripts/safety_receipts.py` first.
- If `patch_retry` present and a failed patch occurs: reread exact target before
  retry; stop/replan after retry limit.
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

## Narration / walkthrough (always on)

- Narrate each build step as a robot walkthrough in plain lines — "Making the
  login page now." then "Done." then "Next: …"
- One short line per step. No code shown, no file paths, no jargon unless user asks.
- Step fails: one plain line — what broke + what you try next. Never hide it.
- Long work: run `scripts/walkaway_pack.py --goal`, then native `/goal`.
- Git: run `scripts/git_workflow.py --mode auto|manual --dry-run`; user approves real git.

## Worktree for risky work

Big refactor: tell user Worktree mode (safe copy; Handoff merges). Git only;
no Git → local with care.

## Evidence rules

- Do not hardcode test counts in docs. Say "all tests green"; let CI show the number.

## tool_interop

tool_interop execute bindings: use installed skill; ACC redirect only;
PRECHECK fail → local ACC + reason.
