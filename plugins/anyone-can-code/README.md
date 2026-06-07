# Anyone Can Code

Docs-native Codex Windows plugin for taking a user from any starting point to a verified result.

## What changed

- One front door plus a small helper surface.
- Bundled MCP memory is now the main durable learning path.
- Bundled plugin hooks stay opt-in and signal-first.
- Project-owned workflow data now lives under `.codex/anyone-can-code/`.
- Setup, update, and diagnostics now follow the Codex Windows plugin model more closely.

## Core workflow

- front door: `$orchestrator` or a natural-language request
- optional detection/bootstrap: `$onboard`
- intake only when needed: `$clarify`
- planning only when needed: `$plan`
- implementation: `$execute`
- evidence-first completion: `$verify`
- recovery: `$resume`
- durable learnings: `$learn`
- user controls: `$status`, `$settings`, `$usage`, `$update`

## Install model

1. Add the marketplace with `codex plugin marketplace add <marketplace-source>`.
2. Install the plugin through the Codex plugin browser from that marketplace.
3. Restart Codex after changing the plugin source used by your marketplace.
4. Open a new thread after install or update so the installed runtime refreshes.
5. Open a project and run `$setup`.
6. If you want bundled plugin hooks, enable Codex `plugin_hooks` and trust the hook bundle.
7. If you want repo-local hook files in addition to bundled hooks, run `$setup --project-hooks`.

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

Workflow:

1. edit plugin code in `plugin source root`
2. keep marketplace pointing at `./plugins/anyone-can-code`
3. bump plugin version when behavior changes
4. refresh plugin through the Codex managed marketplace or plugin browser
5. restart Codex
6. open new thread
7. run `$update` in the repo root if project state needs migration

Plugin-dev repo should stay quiet by default:

- `[features].hooks = false`
- `[features].plugin_hooks = false`
- `[features].memories = false`

Use hooks only when testing hooks on purpose.

## Memory model

- main durable memory: bundled MCP server
- retrieval order: `project -> user -> shared`
- retrieval size: top `3-5` only
- local files: thin fallback only
- learn mode: trigger-auto plus manual `$learn`

## Local data layout

```text
.codex/
  anyone-can-code/
    artifacts/
    backups/
    learning/
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

`$update` compares:

- project state version
- source plugin version
- installed runtime version

If source is newer than runtime, refresh plugin first. Do not migrate yet.

## Troubleshooting

- if a skill path still shows an older version folder, old runtime still active
- if project name shows parent `codex` folder, wrong root open
- if source is newer than runtime, refresh plugin first
- if hooks still run in plugin-dev repo, check project trust, `.codex/config.toml`, and `plugin_hooks`

## Reference files

- `IMPLEMENTATION-SOURCE-OF-TRUTH.md`
- `VALIDATION.md`
