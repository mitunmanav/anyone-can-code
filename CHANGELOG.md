# Changelog

All notable public changes to Anyone Can Code will be documented here.

## 1.1.0-beta.3 - 2026-07-11

Fix-round release. Beta: rough edges expected — please report failures via GitHub Issues.

### Fixed

- `entry_mode` stickiness now survives via an atomic JSON write helper (`canonical_state.atomic_write_json`), fixing a case where the field was silently stripped.
- `audit.py` failure detection now requires a strong signal (non-zero exit code/status, a real traceback, or a timeout) instead of tripping on plain text like "error" or "failed" appearing in command output (e.g. `grep error log.txt`).
- `guard.py`: hard deny checks now always run before the repeat-failure warning, so a denied command can never be downgraded to a warning.
- Doctor rejects being pointed at a file instead of a project root; `build_handoff` catches subprocess errors instead of crashing.
- CLI error paths print to stderr, not stdout.
- Handoff skill uses the `$PLUGIN_ROOT` convention instead of a literal `<plugin>` placeholder.
- Orchestrator skill trimmed to fit the token budget doctor gate.
- Repeat-failure window filters to `command_result` events only; unbounded signal ledger now rotates.
- Per-session style enforcement without hardcoded counts; loop gate text matches spec verbatim.

### Added

- Handoff skill + `build_handoff` script for structured session handoffs.
- Stop-after-2-identical-failures guard, wired into `audit.py`'s real `PostToolUse` handler.

### Housekeeping

- Repo history squashed to a single commit to remove a personal email address that had been committed into history; old `v1.0.0` / `v1.1.0-beta.1` / `v1.1.0-beta.2` tags recreated fresh where still relevant. No file content changed as a result.

### Tests

- 194 tests passing (3 skipped on non-Windows shells).

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

```
codex plugin marketplace add https://github.com/mitunmanav/anyone-can-code
```

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
