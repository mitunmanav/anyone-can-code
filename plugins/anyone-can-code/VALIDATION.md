# Anyone Can Code Validation

## Phase 0 gate

- [ ] Official docs affecting plugins, hooks, skills, MCP, Windows, browser, automations, worktrees, and subagents were read before implementation.
- [ ] `mechanics_docs_gate` was checked before platform mechanics work.
- [ ] Platform mechanics work has a docs brief from official docs/source before code, or controlled proof plus recorded uncertainty when docs/source are missing.
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
- [ ] Every command hook has explicit `timeout` (≤ 60s); never rely on docs default 600s.
- [ ] Portable `command` uses `python3` + `PLUGIN_ROOT` (no PowerShell-only default).
- [ ] Optional `commandWindows` keeps Windows Desktop launcher parity.
- [ ] CLI install path documented: `/plugins` → `/hooks` trust → `$setup`.
- [ ] Hook commands resolve through `PLUGIN_ROOT`/`CLAUDE_PLUGIN_ROOT` in bundled mode and fall back to repo-local plugin source during development.
- [ ] Repo-local hook commands resolve through `.codex/hooks/scripts/` in project mode.
- [ ] Hook scripts emit valid JSON only.
- [ ] Hook logic stays signal-first. No heavy learning write in hooks.
- [ ] An ancestor `.codex/anyone-can-code-hooks.disabled` marker makes every
      ACC hook return `{}` with exit code 0 before any ACC state read/write.
- [ ] ACC-only suppression does not require `[features].hooks = false`; other
      hooks remain enabled.
- [ ] Stop hook writes session snapshots under `.codex/anyone-can-code/state/` and never overwrites root `AGENTS.md`.
- [ ] Every hook attempt writes one durable correlated receipt covering launch,
      script entry, project resolution, returned context/output, state writes,
      skip/failure reason, exit status, duration, and effectiveness.
- [ ] Exit code 0 with empty `{}` output is classified as a no-op, not a pass.
- [ ] Receipt tests prove exact useful output and expected file effects from a
      non-Git workspace root containing one nested ACC project.
- [ ] Controlled app-server QA captures live `hook/started` and
      `hook/completed` run IDs, source paths, events, statuses, timestamps,
      durations, and output entries.
- [ ] Optional consented local OTLP QA captures `codex.hooks.run` and
      `codex.hooks.run.duration_ms` without remote transmission.
- [ ] UI/live events, OTLP metrics, and ACC receipts are compared as separate
      evidence layers; disagreement blocks a healthy claim.

## Windows-first runtime

- [ ] Setup, update, and doctor scripts run with `python` on Windows.
- [ ] No Unix-only paths or shell assumptions remain in core scripts.
- [ ] Bundled hook launchers survive both `cmd.exe /c` and PowerShell outer-shell execution.
- [ ] Bundled hook launchers do not expose PowerShell `$` variables in inline `-Command` strings.
- [ ] WSL is not required for the core build.

## Local data model

- [ ] Project-owned data lives under `.codex/anyone-can-code/`.
- [ ] State, artifacts, learning, settings, logs, backups, and migrations are separated.
- [ ] Workflow state is reconstructable from local artifacts.
- [ ] Canonical workflow state strips stale legacy truth fields including
  `status_line`, `work_state`, `verification_state`, `states`, top-level
  `evidence`, and top-level `unverified`.
- [ ] Doctor reports `legacy_state_fields` as PASS only when raw workflow JSON
  has no legacy truth fields.
- [ ] Durable learning uses linked Markdown as source of truth after migration.
- [ ] Bundled MCP reads/writes Markdown and does not make JSONL the primary store.
- [ ] Rebuildable memory index can be deleted and rebuilt from Markdown.
- [ ] `scripts/memory_preflight.py` can store one learned mistake and retrieve
  it from the selected project memory path.
- [ ] Memory preflight survives setup/update rerun and still returns relevant
  learned mistakes in a new process/thread.
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
- [ ] Existing-site improvement requests route to polish/review, not new-idea intake.
- [ ] Every front-door route includes a response contract requiring visible summary and next action.
- [ ] Every front-door route includes `memory_preflight` requiring
  `Relevant memory used: ...` before questions, plans, specialist routing,
  browser/server work, or tool work.
- [ ] Every front-door route includes `mechanics_docs_gate` so platform mechanics
  work blocks without a docs brief or controlled proof plus uncertainty.
- [ ] Empty or unusable specialist output returns to an ACC fallback response in the same turn.
- [ ] Codex Desktop rendering is not claimed fixed without real-app proof.
- [ ] Idle workspace-root state does not override one meaningful nested ACC project.
- [ ] Meaningfully active requested-root state remains selected when nested candidates are idle.
- [ ] Multiple meaningful ACC projects block with explicit candidate paths.
- [ ] Project discovery is depth-bounded and excludes generated/cache folders.
- [ ] Setup and update resolve active project before state reads or writes.
- [ ] Help, status, and resume resolve project root before reading canonical state.
- [ ] Doctor reports requested, nested-selected, or ambiguous project selection.
- [ ] Specialist mentions or requests do not imply workflow handoff.
- [ ] Every explicitly requested specialist is accounted for as loaded from an exact provider or falling back to ACC with a reason.
- [ ] ACC never claims requested specialist use unless installed metadata and health support it.
- [ ] Every route carries an ACC workflow contract.
- [ ] Project state, memory, preferences, and boundaries load before specialist process actions.
- [ ] Specialist assignments declare advisory process authority and bounded permissions.
- [ ] Nested foreign plan, tracker, approval, commit, route, state, response-style, browser, server, and visual-companion controls are detected.
- [ ] Bounded technical output survives takeover containment.
- [ ] Exact explicit user handoff remains supported.
- [ ] Doctor front-door smoke proves ownership containment.
- [ ] Doctor reports `memory_preflight` as `PASS`.
- [ ] Doctor reports `legacy_state_fields` as `PASS`.
- [ ] Adaptive checklist covers relevant engineering and UX areas with `include`, `defer`, `skip`, or `unknown`.
- [ ] Status uses only `in scope`, `designed`, `approved`, `implemented`, `verified`, `blocked`, or `deferred`.
- [ ] Status reports failures, silent failures, unverified work, uncertainty, route, and next step.
- [ ] Status/help/resume do not trust legacy workflow truth fields when
  canonical verification disagrees.
- [ ] `works` claims for interactive controls require interaction-test evidence.
- [ ] Visual quality, polish, proper, perfect, final, and accepted claims require visual QA or user-acceptance evidence as applicable.
- [ ] Build, source scan, dependency audit, and HTTP smoke evidence are reported as exactly those levels, not as full product success.

## Anti-hallucination rules

- [ ] High-impact unknowns are described as stop-and-ask.
- [ ] Medium-impact unknowns are described as ranked options plus a recommendation.
- [ ] Low-impact safe inference is allowed only when marked.
- [ ] Verification language clearly separates built from verified.
- [ ] `verified` always has evidence; missing checks remain implemented, blocked, or unverified.
- [ ] Unsupported success claims are rewritten to safe wording that lists what passed and what remains unverified.

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
- [ ] `python -m py_compile scripts/memory_preflight.py`
- [ ] `python -m py_compile scripts/product_intake.py`
- [ ] `python -m py_compile scripts/status_model.py`
- [ ] `python -m py_compile scripts/codeburn.py`
- [ ] `python scripts/doctor.py --json` returns a structured report.
- [ ] `doctor.py` reports `product_intake_smoke` as `PASS`.
- [ ] `doctor.py` reports `memory_preflight` as `PASS`.
- [ ] `doctor.py` reports `status_model_smoke` as `PASS`.
- [ ] `doctor.py` reports source root, runtime root, and source/runtime version match or mismatch.
- [ ] `doctor.py` warns when the parent umbrella root looks open instead of the plugin-dev repo.
