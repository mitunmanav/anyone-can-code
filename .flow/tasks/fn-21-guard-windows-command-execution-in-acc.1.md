Description

Implement the Windows command guard described by `fn-21`. Guard ACC planning and docs against three observed raw-session failures: PowerShell execution policy blocking `npm.ps1`, Bash `||` syntax in PowerShell, and Git run from a non-repo workspace parent.

Acceptance

- [ ] Route metadata exposes a Windows-safe command guard.
- [ ] PowerShell npm guidance prefers `npm.cmd`.
- [ ] Bash-only `||` is rejected or replaced in PowerShell guidance.
- [ ] Git guidance requires resolved repo root before Git commands.
- [ ] Orchestrator/bridge/status/verify docs require command guard before shell/server/browser/package/Git work.
- [ ] Doctor or verification surface reports command guard presence.
- [ ] Focused tests cover the three raw-session failure modes.
- [ ] Full tests, compile, Doctor, and Flow validation pass.
- [ ] Obsidian and Flow evidence are updated.

## Description
TBD

## Acceptance
- [ ] TBD

## Done summary
Windows command guard implemented. ACC guidance now prefers npm.cmd on Windows, blocks Bash-only || in PowerShell guidance, and requires repo-root resolution before Git commands.
## Evidence
- Commits:
- Tests: 144 unittest tests OK
- PRs: