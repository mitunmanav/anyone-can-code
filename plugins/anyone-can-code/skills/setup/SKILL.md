---
name: setup
description: "Bootstrap project-owned state for Anyone Can Code. Creates local workflow, learning, settings, and artifact folders, and can optionally install repo-local hooks."
---

# Setup

Use `$setup` after the plugin is installed in Codex.

Reply rule:

- talk strict caveman only
- keep answer short

## What it does

- Explains ordinary Markdown storage, shows path, and offers `none` or optional
  `obsidian` viewer before execution.
- Asks user to confirm or change storage path.
- Defaults to no viewer. ACC remains fully usable.
- Detects Obsidian without launching it.
- Offers viewer actions separately: no action, official download page,
  consented `winget` install, or consented vault-open request.
- Shows every selected session path and scope. Uses preview unless user
  explicitly confirms import.
- Creates `.codex/anyone-can-code/` for state, artifacts, learning, logs, backups, migrations, and portable Markdown memory.
- Creates default preferences with builder persona, `caveman-strict` communication mode, assisted automation, local-first research, automatic plugin routing, and trigger-auto learning.
- Creates memory defaults: path `.codex/anyone-can-code/memory/notes`, viewer mode `none`, import scope `ask`, and production-repo caution on.
- Stores persona once as `builder`, `developer`, or `mixed`; future ACC flow auto-configures tone, depth, approvals, and routing from that setting.
- Writes an install record that tracks plugin version, hook mode, portable Markdown memory mode, memory path, and viewer mode.
- Selected session import snapshots every source before write, skips duplicate
  content on rerun, verifies Markdown, and writes success or rollback receipt.
- Keeps Codex memories off in the plugin-development reference config.
- ACC-only hook suppression uses an ancestor
  `.codex/anyone-can-code-hooks.disabled` marker so unrelated hooks remain active.
- Skips `AGENTS.md` in repo root by default. Use `--agents-md write` to create it (never overwrites existing file).
- Optionally installs repo-local hooks with `$setup --project-hooks`.
- Runs `doctor.py` so the project gets an immediate health report.
- Writes plain Markdown and JSON setup receipts under
  `.codex/anyone-can-code/state/receipts/`.

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

After setup, run `python "$PLUGIN_ROOT/scripts/action_suggest.py"` logic via
the module (`action_suggest.suggest_actions`) for this project. If it returns
suggestions, tell the user in plain words: "Add one-click buttons: Codex
Settings -> Actions -> paste the script." Show each name + script + why.
NEVER write app settings yourself — suggest, user clicks.
