# Anyone Can Code

Docs-native Codex Windows plugin for taking a user from any starting point to a verified result.

## What changed

- One front door plus a small helper surface.
- Portable linked Markdown is the durable memory contract. The bundled MCP
  remains the access interface while the legacy JSONL store becomes migration
  input only.
- Bundled plugin hooks stay opt-in and signal-first.
- Project-owned workflow data now lives under `.codex/anyone-can-code/`.
- Setup, update, and diagnostics now follow the Codex Windows plugin model more closely.

## Core workflow

- front door: `$orchestrator` or a natural-language request
- deterministic route helper: `scripts/front_door.py`
- installed-plugin bridge: manifest scan first, ACC fallback on missing/null coverage
- optional detection/bootstrap: `$onboard`
- intake only when needed: `$clarify`
- planning only when needed: `$plan`
- implementation: `$execute`
- evidence-first completion: `$verify`
- recovery: `$resume`
- durable learnings: `$learn` through portable Markdown memory
- user controls: `$status`, `$settings`, `$usage`, `$update`

Front-door routes cover idea, written spec, existing repo, feature, bug,
polish/review, ship/verify, and mid-work requirement changes. User-visible
output stays compact:

```text
Detected: existing repo + feature request
Route: plan -> execute -> verify
```

Plugin discovery reads installed manifests and skill descriptions only. It does
not execute third-party plugin code while deciding where to route.

## Install model

1. Add the marketplace with `codex plugin marketplace add <marketplace-source>`.
2. Install the plugin through the Codex plugin browser from that marketplace.
3. Restart Codex after changing the plugin source used by your marketplace.
4. Open a new thread after install or update so the installed runtime refreshes.
5. Open a project and run `$setup`.
6. Confirm Markdown storage. Choose no viewer or optional Obsidian. Viewer
   choice alone never launches or installs anything.
7. Existing session files stay untouched unless exact paths, scope, preview,
   and import confirmation are supplied.
8. If you want bundled plugin hooks, enable Codex `plugin_hooks` and trust the hook bundle.
9. If you want repo-local hook files in addition to bundled hooks, run `$setup --project-hooks`.

For plugin development from a local checkout of this repo:

```powershell
codex plugin marketplace add "<path-to-this-repo>"
```

For the app's "upgrade all marketplaces" path, publish this marketplace repo to Git and add the Git source instead:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Official Codex docs say `codex plugin marketplace upgrade` refreshes configured Git marketplaces. Local marketplace sources are tracked by Codex for development, but source edits still need restart or reinstall.

## Develop this plugin with itself

Use one repo root only.

- Open the repo root as the Codex project.
- Do not use the parent umbrella `codex` folder for plugin-dev chats.

Root truth:

- `project root`: repo where you work
- `marketplace root`: repo with `.agents/plugins/marketplace.json`
- `plugin source root`: `./plugins/anyone-can-code`
- `installed plugin root`: `~/.codex/plugins/cache/...`

ACC repository maintainers should keep implementation, candidate testing, and
stable local `main` in separate Git worktrees. Repository-specific tracking and
publishing rules belong in the repository root `AGENTS.md` and
`DEVELOPMENT-WORKFLOW.md`; they must not be copied into user projects.

Workflow:

1. edit plugin code in `plugin source root`
2. keep marketplace pointing at `./plugins/anyone-can-code`
3. bump plugin version when behavior changes
4. refresh plugin through the Codex managed marketplace or plugin browser
5. restart Codex
6. open new thread
7. run `$update` in the repo root if project state needs migration

ACC hook behavior in its development workspace:

- Put `.codex/anyone-can-code-hooks.disabled` at the root of a development
  tree that must not run ACC hooks.
- The marker applies to that folder and every descendant repo/worktree.
- ACC hook scripts return empty success before reading or writing ACC state.
- Other Codex and plugin hooks remain enabled.
- `[features].memories = false`

The ACC source workspace uses the marker at:

```text
C:\Users\Mitun Manav G Y\Desktop\Plugin development\.codex\anyone-can-code-hooks.disabled
```

Remove or rename that marker only when testing ACC hooks on purpose and only
after explicit approval.

## Memory model

- durable memory: linked Markdown files under user-visible ACC storage
- access interface: bundled MCP server
- machine index: rebuildable cache only, never durable truth
- session import: explicit selected paths only, receipt-backed
- migration safety: source snapshot/backup before write, hash dedupe,
  Markdown verification, rollback receipt, originals retained
- retrieval order: `project -> user -> shared`
- retrieval size: top `3-5` only
- viewer: optional; ACC works with no viewer
- Obsidian: optional third-party viewer, never bundled, only offered after
  explicit consent
- setup receipts: unique Markdown and JSON records under
  `.codex/anyone-can-code/state/receipts/`
- ACC viewer: future work, unavailable now
- existing session files: import sources only after explicit user selection
- learn mode: trigger-auto plus manual `$learn`
- full contract: `MEMORY-CONTRACT.md`

## Local data layout

```text
.codex/
  anyone-can-code/
    artifacts/
    backups/
    learning/                 tiny fallback ledgers plus legacy migration inputs
    memory/
      notes/                  target linked Markdown durable memory
        project/
        user/
        shared/
        lessons/
        failures/
        decisions/
        evidence/
        archive/
      index/                  rebuildable machine index, not durable truth
      imports/                backups, snapshots, transactions, and receipts
    migrations/
    settings/
      preferences.json
    state/
      install.json
      state-current.md
      turn-ledger.jsonl
      workflow.json
    logs/
      signal-ledger.jsonl
      mistake-ledger.jsonl
```

## Design rules

- Evidence first.
- No silent assumptions for meaningful decisions.
- Built is not verified.
- Visible talk can be caveman. Hidden reasoning control is not promised.
- Windows-first scripts and paths.
- Optional integrations should degrade safely.

## Upgrade model

Anyone Can Code treats upgrades as three separate layers:

1. refresh the plugin marketplace/source in Codex
2. restart Codex or open a new thread so the installed runtime refreshes
3. run `$update` to migrate project-owned data

Use Codex marketplace management for layer 1. Use `$update` only for layer 3.

During layer 3, `$update` migrates only known ACC-owned legacy JSONL memory.
It backs up before writing, keeps old files after verification, skips duplicate
content on repeated runs, and writes a success or rollback receipt. Existing
Codex/session files are never scanned here; those still require explicit setup
paths, scope, preview, and confirmation.

`$update` compares:

- project state version
- source plugin version
- installed runtime version

If source is newer than runtime, refresh plugin first. Do not migrate yet.

## Troubleshooting

- if a skill path still shows an older version folder, old runtime still active
- if project name shows parent `codex` folder, wrong root open
- if source is newer than runtime, refresh plugin first
- if ACC hooks run below a disabled tree, verify the parent
  `.codex/anyone-can-code-hooks.disabled` marker exists and restart Codex

## Reference files

- `IMPLEMENTATION-SOURCE-OF-TRUTH.md`
- `VALIDATION.md`
- `MEMORY-CONTRACT.md`
