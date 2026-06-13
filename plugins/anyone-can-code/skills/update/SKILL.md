---
name: update
description: "Migrates project state to the current plugin version after the plugin source is refreshed in Codex. Backs up supported data, quarantines corrupt files, and records a migration journal."
---

# Update

Use `$update` after you refresh the plugin through Codex marketplace management and restart or open a new thread.

Reply rule:

- talk strict caveman only
- keep answer short
- say plain truth fast

## What it does

- Compares project state version, source plugin version, and installed runtime version.
- Backs up project-owned state, artifacts, learning, settings, logs, and `AGENTS.md`.
- Quarantines corrupt workflow files instead of overwriting them silently.
- Re-runs setup in the previously chosen hook mode and restores MCP-first memory metadata.
- Migrates only known ACC-owned legacy JSONL memory into linked Markdown.
- Backs up legacy input first, skips duplicate content, verifies Markdown, and
  keeps the legacy file after success.
- Writes success or rollback receipts under `memory/imports/`.
- Writes a migration journal under `.codex/anyone-can-code/migrations/`.
- Runs `doctor.py` after migration.

## What it does not do

- It does not refresh the plugin marketplace/source inside Codex.
- It does not mutate the Codex plugin cache directly.
- It does not scan or import arbitrary Codex/session files.
- It does not replace `codex plugin marketplace add` or `codex plugin marketplace upgrade`.

## Root truth

- `project root`: repo where work happens
- `marketplace root`: repo with `.agents/plugins/marketplace.json`
- `source root`: local editable plugin folder
- `runtime root`: installed cache copy Codex is using

If source is newer than runtime, stop and tell user to refresh plugin through Codex marketplace management first.

Official Codex docs flow:

- add tracked marketplace: `codex plugin marketplace add <source>`
- refresh Git marketplaces: `codex plugin marketplace upgrade`
- local marketplaces are tracked, but local source edits need restart or reinstall
- for app "upgrade all marketplaces", use a Git marketplace source, not a local dev source

## Use when

- The plugin bundle was updated and the project needs migration.
- You want a safe upgrade path with backups and compatibility notes.
