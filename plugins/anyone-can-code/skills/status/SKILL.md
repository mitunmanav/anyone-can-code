---
name: status
description: "Summarizes the current workflow state, route, blockers, and next step from local plugin files."
---

# Status

Use `$status` for a compact checkpoint.

Reply rule:

- talk strict caveman only
- keep answer short

Run `python "$PLUGIN_ROOT/scripts/runtime_info.py" --resolve-project "."`
before reading state. Use returned `project_root`. If result is `ambiguous`,
stop and show candidates instead of choosing or reporting root state.

Read canonical `.codex/anyone-can-code/state/workflow.json` first.
`state-current.md` is derived and must carry same transaction ID.
Treat canonical `verification`, `active_task`, `next_action`, `recovery`, and
`transaction_id` as truth. Ignore legacy truth fields such as `status_line`,
`work_state`, `verification_state`, `states`, top-level `evidence`, and
top-level `unverified` if they appear.

Also read:

- `.codex/anyone-can-code/artifacts/VERIFICATION.md` if present
- `.codex/anyone-can-code/state/install.json`
- source manifest if repo has `.agents/plugins/marketplace.json`
- installed cache manifest if found under `~/.codex/plugins/cache/...`

Return:

- status from canonical verification and tasks, using only closed words:
  `in scope`, `designed`, `approved`, `implemented`, `verified`, `blocked`,
  `deferred`
- active task
- next action
- project root
- source version
- runtime version
- memory mode: `portable-markdown` or fallback
- memory storage health and latest migration/import receipt status
- viewer mode: `none`, `obsidian`, or future `acc-viewer` unavailable
- failures
- silent failures
- unverified work
- remaining uncertainty
- blockers or missing evidence
- evidence levels checked, especially interaction test, visual QA, and user
  acceptance when user-facing quality is being discussed
- active-task capsule saved time and next action
- canonical transaction ID and any derived-view disagreement
- legacy truth fields found, if any, as a repair warning
- command_guard state when command, package-manager, browser, server, Git, or
  tool work is active
- Windows command safety: `npm.cmd` required in PowerShell, Bash-only `||`
  avoided, and repo root resolved before Git commands
- failed command attempts that still need visible recovery
- usage_checkpoint state: below 85% can continue, 85% needs checkpoint, 90%
  needs split, and 94% needs stop-now unless the user explicitly chooses to
  continue
- patch_retry state: failed patch count, whether exact target reread happened,
  whether retry is allowed, and whether stop/replan is required after repeated
  failed patch attempts
- mechanics_docs_gate state: whether work touches platform mechanics, whether
  a docs brief exists, whether controlled proof has recorded uncertainty, and
  whether code changes are blocked

Never use `done`, `complete`, `finished`, or similar words as workflow states.
Example: `Status: build implemented, tests verified, deploy blocked`.
Never report `works`, `proper`, `perfect`, or user accepted unless matching
interaction, visual QA, or user-acceptance evidence is recorded.

## Host

This is the **Desktop** package. CLI users install **Anyone Can Code CLI** (same marketplace). Other agents = later.

## Past questions

"What did we decide about X?" — do not shrug. Run
`python "$PLUGIN_ROOT/scripts/past_answer.py" "<keywords>"` and answer with
the date of each record. Nothing found: say "no record" honestly.
