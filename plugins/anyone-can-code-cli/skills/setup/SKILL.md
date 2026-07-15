---
name: setup
description: "Bootstrap project-owned state for Anyone Can Code. Creates local workflow, learning, settings, and artifact folders, and can optionally install repo-local hooks."
---

# Setup

Use `$setup` after the plugin is installed in Codex.

Reply rule:

- talk strict caveman only
- keep answer short

## Host (CLI package)

This package is **Codex CLI only**. Desktop users install **Anyone Can Code** (Desktop) from the same marketplace.
CLI: `codex` → `/plugins` → install **Anyone Can Code CLI** → `/hooks` trust → `$setup`.
Optional: `codex plugin marketplace add <repo|path>`. No trust = hooks do nothing.

## What it does

- Markdown storage path; viewer `none` (default) or optional `obsidian`.
- Creates `.codex/anyone-can-code/` (state, artifacts, learning, logs, memory).
- Defaults: caveman-strict, persona knobs, automations off until user says yes.
- Session import only after path/scope/confirm; snapshot + receipt.
- Optional `$setup --project-hooks`; `--agents-md write` (never overwrite).
- Runs `doctor.py`; writes receipts under `state/receipts/`.

## Consent

- Never infer consent from viewer selection.
- Never add package/source agreement acceptance flags.
- Never install, download, launch, open a vault, import sessions, move files,
  delete files, or change registry without matching user approval.
- If vault opening is unavailable, show: open Obsidian, choose
  `Open folder as vault`, then select chosen memory folder.
- Declined or failed viewer setup does not block ACC.

## Script mapping

- Storage: `--memory-path <folder>`
- Viewer: `--viewer none|obsidian`
- Viewer action: `--viewer-action none|download-page|install|open-vault`
- Viewer consent: `--consent-viewer-action`
- Import selection: repeat `--import-source <path>`
- Import scope: `--import-scope ask|project|user|shared`
- Import consent: `--confirm-import`
- AGENTS.md: `--agents-md skip|write` (default: skip; never overwrites existing file)

## Hook modes

- Default: portable Markdown memory plus optional bundled plugin hooks from the plugin manifest.
- Optional: repo-local hooks under `.codex/hooks/` for projects that want local lifecycle control.

## Use when

- First project bootstrap after plugin install.
- You want repo-local hooks in addition to bundled plugin hooks.
- You want to repair missing project-owned state folders.

## Action buttons (suggest only)

After setup, use `action_suggest.suggest_actions`. If suggestions: plain words —
"Codex Settings → Actions → paste script." Desktop-first UI; CLI can run same
scripts in terminal. NEVER write app settings yourself.
