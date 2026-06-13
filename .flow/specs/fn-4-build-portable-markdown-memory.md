# Build portable Markdown memory and optional viewers

## Goal & Context

ACC durable memory must be readable without ACC, Obsidian, or a private decoder. Markdown files are the source of truth. Links between notes must support graph-capable viewers, but viewing memory is optional.

Users receive three choices:

1. No viewer. ACC stores linked Markdown and works normally.
2. Obsidian viewer. ACC may offer an explicit official installation or opening flow, but never bundles Obsidian.
3. Future ACC-owned viewer. This is a separate later spec and not part of the current implementation.

## Architecture

- Portable linked Markdown is core storage.
- Bundled MCP reads and writes Markdown.
- Rebuildable machine index may improve retrieval, but cannot become durable truth.
- Memory scopes remain project, user, and shared.
- Existing local Codex/session transcript files are import sources, not hidden
  durable truth. ACC must ask before reading/importing them.
- Markdown remains usable by any file-capable agent.
- Obsidian is optional third-party software, not an ACC dependency.
- ACC-owned viewer is future work.

## Viewer Contract

- User can choose no viewer.
- If Obsidian is already installed, ACC may offer to open the vault.
- If Obsidian is absent, ACC may offer:
  - install from an official source after explicit consent;
  - open official download page;
  - continue without Obsidian.
- ACC does not package, redistribute, modify, or impersonate Obsidian.
- ACC does not silently accept third-party agreements.
- ACC does not claim partnership or affiliation with Obsidian.
- Existing-folder vault registration remains a visible user action unless a supported official mechanism is verified.

## Acceptance Criteria

- **M1:** Durable lessons are linked, readable Markdown.
- **M2:** ACC works fully with no viewer installed.
- **M3:** Any file-capable agent can read the memory.
- **M4:** Obsidian is optional and separately identified as third-party software.
- **M5:** ACC never bundles or redistributes Obsidian binaries or installers.
- **M6:** Installation, download-page opening, app launch, and vault opening require explicit consent.
- **M7:** Declining Obsidian does not block setup, learning, retrieval, migration, or verification.
- **M8:** Setup records selected viewer mode: none, Obsidian, or future ACC viewer unavailable.
- **M9:** Existing JSONL memory migrates with backup, deduplication, receipt, verification, and rollback.
- **M10:** Retrieval returns only the top 3-5 advisory lessons.
- **M11:** Search index is disposable and rebuildable from Markdown.
- **M12:** Doctor reports storage health separately from optional viewer availability.
- **M13:** Windows tests cover no-viewer, Obsidian-present, Obsidian-absent, declined-install, failed-install, and manual vault-open paths.
- **M14:** Maintainer project vault and end-user memory remain separate.
- **M15:** User-selected existing local session files import into linked
  Markdown with backup, deduplication, provenance, scope labels, and receipt.
- **M16:** Prior completed task surfaces from `fn-1` `.1` through `.4` are
  audited and updated so no user-facing path promises JSONL as primary memory.
- **M17:** Memory settings include storage path, viewer mode, import sources,
  import scope, and production-repo caution defaults.

## Boundaries

- No full ACC-owned viewer in this spec.
- No Obsidian binary redistribution.
- No forced third-party installation.
- No hidden download, process launch, registry change, agreement acceptance, migration, move, or overwrite.
- No Obsidian account, Sync, Publish, CLI, community plugin, or paid service requirement.
- No secrets in memory notes.
- No deletion of legacy memory before verified migration and rollback proof.
- No reading/importing existing session files without explicit user-selected
  source paths.

## Prior Task Repair Contract

Tasks `fn-1-define-project-direction.1` through `.4` remain done. This spec
does not reopen their completed implementation unless a user-facing memory
surface is wrong. Task `.4` owns the sweep across setup, update, Doctor, learn,
status, help, onboard, orchestrator, README, validation, and generated state so
all old JSONL/MCP-first promises become portable Markdown promises.

## Quick Commands

```powershell
python -m unittest discover -s plugins\anyone-can-code\tests -p test_*.py
python plugins\anyone-can-code\scripts\doctor.py --json
python .flow\bin\flowctl.py validate --all --json
```
