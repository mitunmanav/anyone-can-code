# Anyone Can Code

Docs-native Codex Windows plugin for taking a user from any starting point to a verified result.

## What changed

- One front door plus a small helper surface.
- Portable linked Markdown is the durable memory contract. The bundled MCP
  remains the access interface while the legacy JSONL store becomes migration
  input only.
- Bundled plugin hooks stay opt-in, measured, signal-first, and non-essential.
- Project-owned workflow data now lives under `.codex/anyone-can-code/`.
- Setup, update, and diagnostics now follow the Codex Windows plugin model more closely.

## Core workflow

- front door: `$orchestrator` or a natural-language request
- deterministic route helper: `scripts/front_door.py`
- installed-plugin bridge: manifest scan, bounded specialist assignment, ACC
  ownership, health probe, takeover blocking, fallback on missing, unhealthy,
  failed, or null coverage, and visible accounting for each requested
  specialist
- workflow containment: specialist mentions never imply handoff; project
  context loads first; specialist process stays advisory; nested foreign plans,
  gates, state, route, browser/server, and visual-companion controls are removed
  while bounded technical output is kept
- routed-response contract: every meaningful route requires visible summary
  and next action; empty specialist output returns to an ACC fallback response
- memory preflight: active project is resolved and `scripts/memory_preflight.py`
  recalls top relevant learned mistakes/preferences before any question, plan,
  specialist route, browser/server action, or tool action; output must include
  `Relevant memory used: ...` or `Relevant memory used: none found`
- active-project resolution: setup, update, help, status, resume, and Doctor
  resolve bounded nested ACC state before reads or writes; one clear active
  project is selected and multiple plausible projects block
- restart recovery: canonical active-task capsule, transaction checks, derived
  view repair, and explicit uncertainty reporting
- canonical-state cleanup: stale legacy workflow truth fields such as
  `status_line`, `work_state`, `verification_state`, `states`, and top-level
  `evidence` are stripped from canonical workflow JSON; Doctor reports any raw
  legacy truth that remains
- bounded task coordination: named tasks carry dependencies, owner, status,
  claim lock, and evidence; duplicate active work is blocked
- subagent coordination: ACC only creates bounded subagent assignments after
  explicit user request and a Codex need, with concise evidence returning to ACC
- optional hook helpers: each hook records one purpose, pass/fail/skipped
  health, bounded retry state, and circuit-breaker status
- safety receipts: important actions write readable JSON/Markdown receipts;
  risky local work needs approval plus rollback; remote work needs exact user
  authority evidence
- Git/GitHub/rollback guardrails: exact workflow state plus receipts decide
  what can be claimed; remote action still requires explicit user command
- usage and background visibility: large reads and loops get approximate cost
  estimates, tool output is compacted into receipts, and background work must
  be visible, stoppable, bounded, and receipt-producing
- optional detection/bootstrap: `$onboard`
- intake only when needed: `$clarify`
- planning only when needed: `$plan`
- implementation: `$execute`
- evidence-first completion: `$verify`
- recovery: `$resume`
- durable learnings: `$learn` through portable Markdown memory
- user controls: `$status`, `$settings`, `$usage`, `$update`

Front-door routes cover idea, written spec, existing repo, feature, bug,
polish/review, ship/verify, and mid-work requirement changes. User-visible
output stays compact:

```text
Detected: existing repo + feature request
Relevant memory used: 2 item(s)
Route: plan -> execute -> verify
```

Existing-site improvement wording routes to polish/review instead of new-idea
intake. ACC requires model output, but Codex Desktop rendering remains
platform-owned and needs separate real-app proof.

When Codex opens a workspace above the real project, run:

```powershell
python "$PLUGIN_ROOT/scripts/runtime_info.py" --resolve-project "."
```

Generated/cache folders, `.worktrees`, and symlinks are excluded. Scanning
stops after three levels. Ambiguous results require explicit project choice.

Plugin discovery reads installed manifests and skill descriptions only. It does
not execute third-party plugin code while deciding where to route.

Every front-door result carries `workflow_contract`. Ownership changes only
after exact user handoff. Specialist assignments state allowed output,
permissions, forbidden actions, process authority, and return path.
When a user names specialists, the front door records each one under
`requested_specialists` as either matched to an exact installed provider or
falling back to ACC with a reason.
The front door also carries `memory_preflight`; installed ACC must run the
script and show the memory line before it chooses skills or asks the user what
to do.

## Install model

1. Add the marketplace with `codex plugin marketplace add <marketplace-source>`.
2. Install the plugin through the Codex plugin browser from that marketplace.
3. Restart Codex after changing the plugin source used by your marketplace.
4. Open a new thread after install or update so the installed runtime refreshes.
5. Open a project and run `$setup`.
6. Confirm Markdown storage. Choose no viewer or optional Obsidian. Viewer
   choice alone never launches or installs anything.
7. Existing session files stay untouched unless exact paths, scope, preview,
   and import confirmation are supplied.
8. If you want bundled plugin hooks, enable Codex `plugin_hooks` and trust the hook bundle.
9. If you want repo-local hook files in addition to bundled hooks, run `$setup --project-hooks`.

For plugin development from a local checkout of this repo:

```powershell
codex plugin marketplace add "<path-to-this-repo>"
```

For the app's "upgrade all marketplaces" path, publish this marketplace repo to Git and add the Git source instead:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Official Codex docs say `codex plugin marketplace upgrade` refreshes configured Git marketplaces. Local marketplace sources are tracked by Codex for development, but source edits still need restart or reinstall.

## Develop this plugin with itself

Use one repo root only.

- Open the repo root as the Codex project.
- Do not use the parent umbrella `codex` folder for plugin-dev chats.

Root truth:

- `project root`: repo where you work
- `marketplace root`: repo with `.agents/plugins/marketplace.json`
- `plugin source root`: `./plugins/anyone-can-code`
- `installed plugin root`: `~/.codex/plugins/cache/...`

ACC repository maintainers should keep implementation, candidate testing, and
stable local `main` in separate Git worktrees. Repository-specific tracking and
publishing rules belong in the repository root `AGENTS.md` and
`DEVELOPMENT-WORKFLOW.md`; they must not be copied into user projects.

Workflow:

1. edit plugin code in `plugin source root`
2. keep marketplace pointing at `./plugins/anyone-can-code`
3. bump plugin version when behavior changes
4. refresh plugin through the Codex managed marketplace or plugin browser
5. restart Codex
6. open new thread
7. run `$update` in the repo root if project state needs migration

ACC hook behavior in its development workspace:

- Put `.codex/anyone-can-code-hooks.disabled` at the root of a development
  tree that must not run ACC hooks.
- The marker applies to that folder and every descendant repo/worktree.
- ACC hook scripts return empty success before reading or writing ACC state.
- ACC hooks are helpers only. Core workflow uses canonical state and continues
  when hooks are absent, fail, or trip their circuit breaker.
- Hook health is stored in `.codex/anyone-can-code/logs/hook-health.json` and
  `.codex/anyone-can-code/logs/hook-health-ledger.jsonl`.
- Durable hook receipts must record correlation ID, session/turn ID, hook name,
  launch and script-entry timestamps, project-resolution result, returned
  context/output summary, state-write paths, skip/failure reason, exit status,
  duration, and final effectiveness state. Exit code zero with `{}` is a
  measured no-op, not healthy execution.
- Strong hook QA combines three separate signals when available: live Codex
  `hook/started`/`hook/completed` notifications, consented local OTLP metrics
  (`codex.hooks.run` and `codex.hooks.run.duration_ms`), and ACC receipts.
  No single signal proves useful effect by itself.
- IMPORTANT deferred state: rollout JSONL is not a complete hook-run ledger.
  System prompts, normal developer messages, collaboration-mode messages, and
  plugin capability injections are not hook proof. Resume this work through
  `fn-14-make-acc-hooks-effective-from-non-git`; do not infer silent runs.
- Hook repair retries stop after two consecutive failures. Fixed claims require
  restart or new-thread proof, not just edited source.
- Hook launcher repairs must pass both `cmd.exe /c` and PowerShell outer-shell
  execution in the installed cache.
- Risky and remote actions must pass the safety receipt gate before execution.
- Hook launchers accept either the plugin directory or its marketplace
  repository root and resolve the nested `plugins/anyone-can-code` directory.
- Other Codex and plugin hooks remain enabled.
- `[features].memories = false`

The ACC source workspace uses the marker at:

```text
C:\Users\Mitun Manav G Y\Desktop\Plugin development\.codex\anyone-can-code-hooks.disabled
```

Remove or rename that marker only when testing ACC hooks on purpose and only
after explicit approval.

## Memory model

- durable memory: linked Markdown files under user-visible ACC storage
- access interface: bundled MCP server
- machine index: rebuildable cache only, never durable truth
- session import: explicit selected paths only, receipt-backed
- migration safety: source snapshot/backup before write, hash dedupe,
  Markdown verification, rollback receipt, originals retained
- retrieval order: `project -> user -> shared`
- retrieval size: top `3-5` only
- first-action recall: required before questions, plans, skill routing,
  browser/server work, and tool work
- update/new-thread continuity: `$update` preserves memory path and Doctor
  checks source-level memory preflight
- viewer: optional; ACC works with no viewer
- Obsidian: optional third-party viewer, never bundled, only offered after
  explicit consent
- setup receipts: unique Markdown and JSON records under
  `.codex/anyone-can-code/state/receipts/`
- ACC viewer: future work, unavailable now
- existing session files: import sources only after explicit user selection
- learn mode: trigger-auto plus manual `$learn`
- full contract: `MEMORY-CONTRACT.md`

## Local data layout

```text
.codex/
  anyone-can-code/
    artifacts/
    backups/
    learning/                 tiny fallback ledgers plus legacy migration inputs
    memory/
      notes/                  target linked Markdown durable memory
        project/
        user/
        shared/
        lessons/
        failures/
        decisions/
        evidence/
        archive/
      index/                  rebuildable machine index, not durable truth
      imports/                backups, snapshots, transactions, and receipts
    migrations/
    settings/
      preferences.json
    state/
      install.json
      state-current.md
      turn-ledger.jsonl
      workflow.json
    logs/
      signal-ledger.jsonl
      mistake-ledger.jsonl
```

## Design rules

- Evidence first.
- No silent assumptions for meaningful decisions.
- `mechanics_docs_gate` is a hard gate for platform mechanics changes. Hook,
  plugin runtime, installed cache, Windows launch, UI lifecycle, telemetry/log,
  MCP, and tool-plumbing work needs a docs brief from official docs/source
  before code. If docs/source are missing, controlled proof must record
  uncertainty first. Session traces are failure evidence only.
- Built is not verified.
- Build, source scan, dependency audit, and HTTP smoke do not prove
  interactions, visual quality, or user acceptance.
- Do not claim `works`, `proper`, `perfect`, `final`, or accepted unless the
  matching interaction, visual QA, or user-acceptance evidence exists.
- Usage warnings state uncertainty because transcript and token accounting are
  approximate from local evidence.
- Normal work starts with cheap checks. Deep checks are added when risk, shared
  behavior, or user-visible behavior requires them.
- Source tests alone do not close installed-app guardrails. Installed runtime
  QA receipt must pass first.
- Visible talk can be caveman. Hidden reasoning control is not promised.
- Windows-first scripts and paths.
- Optional integrations should degrade safely.

## Upgrade model

Anyone Can Code treats upgrades as three separate layers:

1. refresh the plugin marketplace/source in Codex
2. restart Codex or open a new thread so the installed runtime refreshes
3. run `$update` to migrate project-owned data

Use Codex marketplace management for layer 1. Use `$update` only for layer 3.

During layer 3, `$update` migrates only known ACC-owned legacy JSONL memory.
It backs up before writing, keeps old files after verification, skips duplicate
content on repeated runs, and writes a success or rollback receipt. Existing
Codex/session files are never scanned here; those still require explicit setup
paths, scope, preview, and confirmation.

`$update` compares:

- project state version
- source plugin version
- installed runtime version

If source is newer than runtime, refresh plugin first. Do not migrate yet.

## Troubleshooting

- Run Doctor first when recovery feels wrong. It checks installed ACC source,
  project state agreement, hook health, memory storage, runtime freshness, and
  plugin conflict ownership. It also checks usage-budget/background-work support.
- If Doctor finds another plugin near ACC workflow ownership, ACC keeps control
  and uses that plugin only as a bounded helper unless the user explicitly hands
  ownership over.
- ACC recovery never edits another plugin silently. If another plugin looks
  broken, the safe next action is to keep ACC fallback running and ask before
  touching that plugin.
- if a skill path still shows an older version folder, old runtime still active
- if project name shows parent `codex` folder, wrong root open
- if source is newer than runtime, refresh plugin first
- if ACC hooks run below a disabled tree, verify the parent
  `.codex/anyone-can-code-hooks.disabled` marker exists and restart Codex
- if every visible ACC hook exits `1`, verify Codex did not supply the
  marketplace repository as `PLUGIN_ROOT`; current launchers normalize it
  before running hook scripts

## Reference files

- `IMPLEMENTATION-SOURCE-OF-TRUTH.md`
- `VALIDATION.md`
- `MEMORY-CONTRACT.md`
