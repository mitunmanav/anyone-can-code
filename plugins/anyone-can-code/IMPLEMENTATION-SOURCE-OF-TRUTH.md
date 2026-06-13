# Anyone Can Code - Implementation Source of Truth

## Reused
- The end-to-end workflow skeleton: onboard, clarify, plan, execute, verify, learn, update.
- The local usage-analysis scripts and the general doctor/setup/update philosophy.
- The project-context file pattern through `AGENTS.md`.

## Refactored
- Plugin manifest now uses bundled hooks and removes the core Obsidian dependency.
- Hooks now support a docs-native bundled mode first, with project bootstrap hooks as an optional setup path.
- Runtime paths now separate plugin-owned writable data from project-owned workflow files.
- Memory contract is portable linked Markdown durability, with bundled MCP as
  the access interface and JSONL only as explicit migration input.
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
- Structured local stores for state, artifacts, portable Markdown memory,
  settings, backups, imports, and migrations.
- `MEMORY-CONTRACT.md` defining Markdown note schema, viewer choices, explicit
  consent boundaries, session import rules, settings, and recovery behavior.
- A migration journal and quarantine flow for incompatible project data.
- Transactional JSONL/session migration with source backups, stable-hash
  deduplication, Markdown verification, and rollback receipts.
- A tighter docs-native foundation for a future front-door orchestrator and helper skills.

## Migration contract

- Existing task `.1` through `.4` product behavior stays accepted.
- Durable memory writes use Markdown. JSONL remains only for small operational
  ledgers and explicit legacy/session migration input.
- User-selected existing session files are import sources only; ACC must ask,
  back up/snapshot, deduplicate, label scope, and write receipts.
- `$update` migrates known ACC-owned legacy memory only. It never scans
  arbitrary session locations.
- Obsidian app is optional third-party viewer only. ACC does not bundle it.
