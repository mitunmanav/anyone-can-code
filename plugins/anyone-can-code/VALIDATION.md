# Anyone Can Code Validation

## Phase 0 gate

- [ ] Official docs affecting plugins, hooks, skills, MCP, Windows, browser, automations, worktrees, and subagents were read before implementation.
- [ ] `IMPLEMENTATION-SOURCE-OF-TRUTH.md` reflects what was reused, refactored, removed, and added.

## Manifest and bundle

- [ ] `.codex-plugin/plugin.json` is valid JSON.
- [ ] `name`, `version`, `description`, `skills`, `hooks`, and `mcpServers` are present.
- [ ] `defaultPrompt` has at most 3 entries and each entry is at most 128 chars.
- [ ] `hooks/hooks.json` exists in the plugin bundle.
- [ ] `.mcp.json` is valid JSON and declares one bundled stdio memory server under `mcpServers`.

## Hook strategy

- [ ] Bundled hook mode works only when Codex `plugin_hooks` is enabled.
- [ ] Project bootstrap hook mode is optional, not required for core plugin function.
- [ ] Hook commands resolve through `PLUGIN_ROOT`/`CLAUDE_PLUGIN_ROOT` in bundled mode and fall back to repo-local plugin source during development.
- [ ] Repo-local hook commands resolve through `.codex/hooks/scripts/` in project mode.
- [ ] Hook scripts emit valid JSON only.
- [ ] Hook logic stays signal-first. No heavy learning write in hooks.
- [ ] An ancestor `.codex/anyone-can-code-hooks.disabled` marker makes every
      ACC hook return `{}` with exit code 0 before any ACC state read/write.
- [ ] ACC-only suppression does not require `[features].hooks = false`; other
      hooks remain enabled.
- [ ] Stop hook writes session snapshots under `.codex/anyone-can-code/state/` and never overwrites root `AGENTS.md`.

## Windows-first runtime

- [ ] Setup, update, and doctor scripts run with `python` on Windows.
- [ ] No Unix-only paths or shell assumptions remain in core scripts.
- [ ] PowerShell-oriented hook command strings are used in bundled hooks.
- [ ] WSL is not required for the core build.

## Local data model

- [ ] Project-owned data lives under `.codex/anyone-can-code/`.
- [ ] State, artifacts, learning, settings, logs, backups, and migrations are separated.
- [ ] Workflow state is reconstructable from local artifacts.
- [ ] Durable learning uses linked Markdown as source of truth after migration.
- [ ] Bundled MCP reads/writes Markdown and does not make JSONL the primary store.
- [ ] Rebuildable memory index can be deleted and rebuilt from Markdown.
- [ ] `MEMORY-CONTRACT.md` defines note schema, viewer modes, settings,
  explicit consent boundaries, and session import receipts.
- [ ] Existing session imports require explicit selected source paths, backup or
  snapshot, deduplication, provenance, scope labels, and receipts.
- [ ] Repeating the same import creates no duplicate note and does not reinforce
  the existing note again.
- [ ] Failed import restores the pre-import Markdown tree, writes a rollback
  receipt, and leaves source data intact.
- [ ] ACC works with no memory viewer installed.
- [ ] Optional Obsidian paths never bundle, redistribute, launch, install, or
  open a vault without explicit consent.
- [ ] Setup preserves chosen memory path and writes a plain-language receipt.
- [ ] Session import is preview-only until explicit confirmation.
- [ ] Obsidian present, absent, declined, and failed-install paths do not block
  no-viewer ACC operation.
- [ ] Consented `winget` install passes no agreement-acceptance flags.
- [ ] Unsupported vault opening shows manual `Open folder as vault`
  instructions.
- [ ] Official download-page action opens only the official URL and never runs
  the installer.
- [ ] Existing memory-path file conflicts fail visibly and preserve the file.
- [ ] Permission-denied legacy migration writes a rollback receipt and
  preserves the source plus existing Markdown.
- [ ] Upgrade stops before setup or journal writes when memory migration rolls
  back.
- [ ] A plain file reader can read note headings and follow normal or
  wiki-style links without ACC.

## Workflow surface

- [ ] One front-door orchestrator skill exists.
- [ ] Helper skills exist for `status`, `resume`, `settings`, `usage`, and `update`.
- [ ] `onboard`, `clarify`, `plan`, `execute`, `verify`, and `learn` point to local workflow files.
- [ ] Fast path and full path are both represented in the skill guidance.
- [ ] Request-to-plan smoke: `python plugins/anyone-can-code/scripts/product_intake.py` prints `Plan: website + auth + deploy. Payments later.`
- [ ] Product intake asks at most five blocking questions and skips known answers.
- [ ] Adaptive checklist covers relevant engineering and UX areas with `include`, `defer`, `skip`, or `unknown`.
- [ ] Status uses only `in scope`, `designed`, `approved`, `implemented`, `verified`, `blocked`, or `deferred`.
- [ ] Status reports failures, silent failures, unverified work, uncertainty, route, and next step.

## Anti-hallucination rules

- [ ] High-impact unknowns are described as stop-and-ask.
- [ ] Medium-impact unknowns are described as ranked options plus a recommendation.
- [ ] Low-impact safe inference is allowed only when marked.
- [ ] Verification language clearly separates built from verified.
- [ ] `verified` always has evidence; missing checks remain implemented, blocked, or unverified.

## Recovery and upgrade

- [ ] `setup.py` creates local workflow state without requiring Obsidian.
- [ ] `update.py` compares project state, source plugin, and installed runtime.
- [ ] `update.py` handles project migration only after runtime refresh.
- [ ] The three-layer upgrade story is documented: distribution refresh, runtime refresh, project migration.
- [ ] Managed marketplace flow is documented from official Codex plugin docs.
- [ ] `doctor.py` reports whether the marketplace is tracked by Codex marketplace management.
- [ ] Corrupt workflow files are quarantined instead of overwritten silently.
- [ ] A migration journal is written during updates.
- [ ] Known ACC-owned legacy JSONL is backed up, migrated, verified, and retained.
- [ ] `$update` does not scan arbitrary user session locations.
- [ ] Doctor reports Markdown storage health separately from optional viewer
  availability.
- [ ] Restart plus new thread are documented after local plugin refresh.
- [ ] Update prints project, source, and runtime versions.
- [ ] Update prints project, marketplace, source, and runtime roots when found.

## Syntax and diagnostics

- [ ] `python -m py_compile mcp/server.py`
- [ ] `python -m py_compile hooks/scripts/state.py`
- [ ] `python -m py_compile hooks/scripts/guard.py`
- [ ] `python -m py_compile hooks/scripts/audit.py`
- [ ] `python -m py_compile hooks/scripts/load_session.py`
- [ ] `python -m py_compile hooks/scripts/save_session.py`
- [ ] `python -m py_compile scripts/setup.py`
- [ ] `python -m py_compile scripts/update.py`
- [ ] `python -m py_compile scripts/doctor.py`
- [ ] `python -m py_compile scripts/product_intake.py`
- [ ] `python -m py_compile scripts/status_model.py`
- [ ] `python -m py_compile scripts/codeburn.py`
- [ ] `python scripts/doctor.py --json` returns a structured report.
- [ ] `doctor.py` reports `product_intake_smoke` as `PASS`.
- [ ] `doctor.py` reports `status_model_smoke` as `PASS`.
- [ ] `doctor.py` reports source root, runtime root, and source/runtime version match or mismatch.
- [ ] `doctor.py` warns when the parent umbrella root looks open instead of the plugin-dev repo.
