# Changelog

All notable public changes to Anyone Can Code will be documented here.

## 2.0.0-beta.4 - 2026-07-20

Desktop plugin only. CLI stays **1.1.0-beta.4**.

### Security / reliability (Desktop hooks)

- Stricter **PermissionRequest** auto-allow: whole command chain must be safe (not only the first prefix).
- Stronger **PreToolUse** blocks for pipe-to-shell and related patterns (`cat|bash`, `echo|sh`, etc.).
- Guard / audit **fail closed** on crash for tool gates (deny + exit 2), matching Codex hooks docs.
- Wire **workflow-takeover** block into PreToolUse (was tested but not called).
- Production mode + force-push flags honored on safety authority path.
- Deploy vs plain `git push` split; quieter silent-failure signals; session-scoped rate/token read when `session_id` present.

### Notes

- Hooks remain a **guardrail** (Codex: Bash / apply_patch / MCP). OS sandbox still required.
- Unit tests + doctor expected green before ship.

## 1.1.0-beta.4 - 2026-07-16

Beta.4 locked-rule finish. Beta: rough edges expected — please report failures via GitHub Issues.

### Added

- **Offline auto-memory (Desktop)** — hooks write wants, decisions, corrections, and open work automatically (no save command). SessionStart injects NOW + crash-resume; durable fsynced journals; FTS5/LIKE note search; memory doctor detects untrusted hooks.
- **Codex CLI package (separate plugin)** — `plugins/anyone-can-code-cli/` full copy, CLI-tuned hooks (`python3` + `PLUGIN_ROOT`, short timeouts); Desktop stays `plugins/anyone-can-code/`; same marketplace lists both; pick the name for your host (Codex does not auto-select).
- **Two-drawer memory** — user taste (style, likes) lives in one global drawer; project lessons stay inside the project. Drawers never mix.
- **Taste guard** — user drawer accepts only `preference` / `pattern`; project facts are rejected in plain words.
- **`$update` user-drawer migration** — taste notes move global; project facts re-scoped, with a receipt. Rerun-safe.
- **Plain-words build narration** — execute/orchestrator narrate steps in plain words; no code shown unless asked.
- **Warm tone + jargon plain** — caveman stays short but not cold; developer jargon auto-swapped for plain words.
- **Layered push-back** — impossible → say no; better way → explain simple, user picks; fine as asked → do it.
- **Permanent locked-rule guards** — skill ≤4000 chars, stdlib-only shipped Python.

### Fixed

- **Session-start lesson recall** — now reads scoped note folders (was non-recursive, found nothing). Capped and ranked; skips revoked.
- **User words like `pending`** — step text kept; task queue maps `pending` → `todo` so the queue never rejects that word.

## 1.1.0-beta.3 - 2026-07-11

Fix-round release. Beta: rough edges expected — please report failures via GitHub Issues.

### Added

- **Real CLIs for `canonical_state.py` and `task_coordination.py`** (`show`, `update --set key=value`, `status`, `claim`, `release`) — no more hand-written inline-Python heredocs to read or update project state.
- **Sticky entry-mode classification** — once a project is classified (idea / existing-repo / bug / etc.), it stays that way instead of re-classifying and flip-flopping every turn. Say "start over" / "new project" / "re-detect" to force a re-check.
- **Task-aware adaptive loop** — requests are scored `micro | bug | feature | research | product` and get a matching loop budget and ceremony level, replacing one fixed process for every request size.
- **Loop real-use checkpoint gate** — after the loop budget is used up, execution stops and asks for real-use proof instead of endlessly polishing docs.
- `setup.py --agents-md {write,skip}` (default `skip`) — setup no longer silently writes an `AGENTS.md` into your repo root; opt in explicitly if you want it.
- `doctor.py` accepts an optional target project path instead of only checking the current directory.
- `memory_preflight.py` gives a clear usage example and a proper exit code on misuse instead of a bare error.
- Handoff skill + `build_handoff` script for structured session handoffs.
- Stop-after-2-identical-failures guard, wired into `audit.py`'s real `PostToolUse` handler.
- Session-start context now always restates "strict caveman, short, direct" so style doesn't drift after long sessions/compaction.
- Execute skill now says "let CI show the test count" instead of hardcoding numbers in docs that go stale.
- Contract test ensures every file path a skill mentions is one setup actually creates.

### Fixed

- `entry_mode` stickiness now survives via an atomic JSON write helper (`canonical_state.atomic_write_json`), fixing a case where the field was silently stripped.
- `audit.py` failure detection now requires a strong signal (non-zero exit code/status, a real traceback, or a timeout) instead of tripping on plain text like "error" or "failed" appearing in command output (e.g. `grep error log.txt`).
- `guard.py`: hard deny checks now always run before the repeat-failure warning, so a denied command can never be downgraded to a warning.
- Doctor rejects being pointed at a file instead of a project root; `build_handoff` catches subprocess errors instead of crashing.
- CLI error paths print to stderr, not stdout.
- Handoff skill uses the `$PLUGIN_ROOT` convention instead of a literal `<plugin>` placeholder.
- Orchestrator skill trimmed to fit the token budget doctor gate.
- Repeat-failure window filters to `command_result` events only; unbounded signal ledger now rotates.

### Housekeeping

- Repo history squashed to a single commit to remove a personal email address that had been committed into history; old `v1.0.0` / `v1.1.0-beta.1` / `v1.1.0-beta.2` tags recreated fresh where still relevant. No file content changed as a result.

### Tests

- Full pytest suite green in CI (`python -m pytest plugins/anyone-can-code/tests -q`). Do not hardcode pass counts in docs.

### Install

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

## 1.1.0-beta.2 - 2026-07-07

Improvement-loop release. Beta: rough edges expected — please report failures via GitHub Issues.

### Added

- Inbox: idea dump with count and already-told detection (`inbox.py`).
- Runtime capability registry (`capabilities.py`): routes to native Codex features instead of rebuilding them; new features picked up automatically.
- Native-feature routing text for terminal, browser, review pane, worktrees, and cloud mode.
- Subagent lifecycle hooks.
- Rule promotion: a lesson seen 3+ times is proposed once; on yes it lands in `memory/rules.md`.
- Past answers: dated answers notes plus ledger.
- User model: about-you profile.
- Action suggestions after each session.
- `PROGRESS.md` render and plugin update nudge.
- Automations README.

### Changed

- Guard token budget capped at 1200; doctor `SKILL_BUDGET_CHARS` 4000.
- Orchestrator and verify skill text trimmed.
- Dictation filler words stripped from input.
- Compact re-anchor keeps goal and next action after context compaction.
- Docs scrubbed of personal file paths.

### Install

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

(Older notes may show a full GitHub URL; the short marketplace form above is preferred.)

## 1.1.0-beta.1 - 2026-07-06

Reliability release driven by a real end-to-end trial session. Beta: rough edges expected — please report failures via GitHub Issues.

### Fixed

- Routing: another installed plugin can no longer hijack a generic request; ACC only routes away when the plugin or skill is named, or the overlap is strong.
- Session summaries no longer get chopped mid-word at 280 characters (now word-boundary at 2000).
- State writes retry up to 3 times on transaction conflicts instead of silently losing updates.
- Shell exit code 124 (timeout) is now treated as "service not ready", never as success.
- Deploys are blocked while `USE_MOCK_DB=true`, with a pre-deploy checklist injected.
- Bundled hook commands on Windows run through an explicit PowerShell launcher, resolve from parent workspace checkouts, and keep working when plugin-root environment variables are missing.

### Added

- Control now rides hooks, not skills: communication rule, active goal, next action, and top lessons are injected every turn — immune to the Codex skills-list cap that made skills vanish in the trial.
- Memory with proof: session start records what was recalled, session end records what was saved; lessons from one session appear in the next.
- Circuit breaker: the same command failing twice stops the run loudly and records the mistake.
- Doctor checks for plugin cache version drift and skills missing from the installed cache.
- Model ledger: session outcomes feed a per-project ledger; the recommended model is surfaced at session start.
- Structured `next_steps[]` checklist in workflow state and the resume capsule.
- Orchestrator and plan skills now instruct Codex literally how to spawn scoped subagents.
- First-run menu (builder / developer / mixed) asked once and persisted; every session ends with a short recap.
- Privacy policy (`PRIVACY.md`) and terms of service (`TERMS.md`).

### Tests

- Suite grown from 158 to 261 passing tests (3 skipped on non-Windows shells).

## 1.0.0 - 2026-06-07

- Prepared the first public release.
- Added a clean top-level README, MIT license, security policy, contribution guide, issue templates, and release workflow.
- Set the public plugin version to `1.0.0`.
- Packaged the plugin bundle through GitHub Actions.
