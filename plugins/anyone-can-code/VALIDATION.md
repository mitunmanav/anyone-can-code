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
- [ ] Hook commands resolve through `PLUGIN_ROOT` in bundled mode.
- [ ] Repo-local hook commands resolve through `.codex/hooks/scripts/` in project mode.
- [ ] Hook scripts emit valid JSON only.
- [ ] Hook logic stays signal-first. No heavy learning write in hooks.

## Windows-first runtime

- [ ] Setup, update, and doctor scripts run with `python` on Windows.
- [ ] No Unix-only paths or shell assumptions remain in core scripts.
- [ ] PowerShell-oriented hook command strings are used in bundled hooks.
- [ ] WSL is not required for the core build.

## Local data model

- [ ] Project-owned data lives under `.codex/anyone-can-code/`.
- [ ] State, artifacts, learning, settings, logs, backups, and migrations are separated.
- [ ] Workflow state is reconstructable from local artifacts.
- [ ] Durable learning is MCP-first and local files stay thin fallback only.

## Workflow surface

- [ ] One front-door orchestrator skill exists.
- [ ] Helper skills exist for `status`, `resume`, `settings`, `usage`, and `update`.
- [ ] `onboard`, `clarify`, `plan`, `execute`, `verify`, and `learn` point to local workflow files.
- [ ] Fast path and full path are both represented in the skill guidance.
- [ ] Request-to-plan smoke: `python plugins/anyone-can-code/scripts/product_intake.py` prints `Plan: website + auth + deploy. Payments later.`
- [ ] Product intake asks at most five blocking questions and skips known answers.
- [ ] Adaptive checklist covers relevant engineering and UX areas with `include`, `defer`, `skip`, or `unknown`.

## Anti-hallucination rules

- [ ] High-impact unknowns are described as stop-and-ask.
- [ ] Medium-impact unknowns are described as ranked options plus a recommendation.
- [ ] Low-impact safe inference is allowed only when marked.
- [ ] Verification language clearly separates built from verified.

## Recovery and upgrade

- [ ] `setup.py` creates local workflow state without requiring Obsidian.
- [ ] `update.py` compares project state, source plugin, and installed runtime.
- [ ] `update.py` handles project migration only after runtime refresh.
- [ ] The three-layer upgrade story is documented: distribution refresh, runtime refresh, project migration.
- [ ] Managed marketplace flow is documented from official Codex plugin docs.
- [ ] `doctor.py` reports whether the marketplace is tracked by Codex marketplace management.
- [ ] Corrupt workflow files are quarantined instead of overwritten silently.
- [ ] A migration journal is written during updates.
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
- [ ] `python -m py_compile scripts/codeburn.py`
- [ ] `python scripts/doctor.py --json` returns a structured report.
- [ ] `doctor.py` reports `product_intake_smoke` as `PASS`.
- [ ] `doctor.py` reports source root, runtime root, and source/runtime version match or mismatch.
- [ ] `doctor.py` warns when the parent umbrella root looks open instead of the plugin-dev repo.
