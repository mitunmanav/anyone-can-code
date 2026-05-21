# Anyone Can Code - Implementation Source of Truth

## Reused
- The end-to-end workflow skeleton: onboard, clarify, plan, execute, verify, learn, update.
- The local usage-analysis scripts and the general doctor/setup/update philosophy.
- The project-context file pattern through `AGENTS.md`.

## Refactored
- Plugin manifest now uses bundled hooks and removes the core Obsidian dependency.
- Hooks now support a docs-native bundled mode first, with project bootstrap hooks as an optional setup path.
- Runtime paths now separate plugin-owned writable data from project-owned workflow files.
- Project state now lives under `.codex/anyone-can-code/` instead of being spread across repo-local hook markers and Obsidian files.
- Setup/update/doctor now reflect the Codex Windows plugin model and the three-layer upgrade path.

## Removed
- Obsidian MCP as a required core dependency.
- The assumption that bundled hooks must be absent.
- The deprecated `codex_hooks` configuration model.
- The requirement that setup must copy hooks before the plugin can function.

## Added
- Bundled `hooks/hooks.json`.
- Windows-safe project bootstrap with optional repo-local hook installation.
- Structured local stores for state, artifacts, learning, settings, backups, and migrations.
- A migration journal and quarantine flow for incompatible project data.
- A tighter docs-native foundation for a future front-door orchestrator and helper skills.
