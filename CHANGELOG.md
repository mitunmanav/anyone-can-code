# Changelog

All notable public changes to Anyone Can Code will be documented here.

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
