---
name: status
description: "Summarizes the current workflow state, route, blockers, and next step from local plugin files."
---

# Status

Use `$status` for a compact checkpoint.

Reply rule:

- talk strict caveman only
- keep answer short

Read canonical `.codex/anyone-can-code/state/workflow.json` first.
`state-current.md` is derived and must carry same transaction ID.

Also read:

- `.codex/anyone-can-code/artifacts/VERIFICATION.md` if present
- `.codex/anyone-can-code/state/install.json`
- source manifest if repo has `.agents/plugins/marketplace.json`
- installed cache manifest if found under `~/.codex/plugins/cache/...`

Return:

- exact status line from the closed states: `in scope`, `designed`, `approved`,
  `implemented`, `verified`, `blocked`, `deferred`
- current phase
- current route
- last task
- next step
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
- active-task capsule saved time and next action
- canonical transaction ID and any derived-view disagreement

Never use `done`, `complete`, `finished`, or similar words as workflow states.
Example: `Status: build implemented, tests verified, deploy blocked`.
