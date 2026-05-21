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

- Creates `.codex/anyone-can-code/` for state, artifacts, learning, logs, backups, and migrations.
- Creates default preferences with `caveman-strict` communication mode, aggressive automation, and trigger-auto learning.
- Writes an install record that tracks plugin version, hook mode, and MCP-first memory mode.
- Keeps plugin-dev repo quiet by default: hooks off, plugin_hooks off, memories off.
- Refreshes `AGENTS.md` from the project template if needed.
- Optionally installs repo-local hooks with `$setup --project-hooks`.
- Runs `doctor.py` so the project gets an immediate health report.

## Hook modes

- Default: bundled MCP memory plus optional bundled plugin hooks from the plugin manifest.
- Optional: repo-local hooks under `.codex/hooks/` for projects that want local lifecycle control.

## Use when

- First project bootstrap after plugin install.
- You want repo-local hooks in addition to bundled plugin hooks.
- You want to repair missing project-owned state folders.
