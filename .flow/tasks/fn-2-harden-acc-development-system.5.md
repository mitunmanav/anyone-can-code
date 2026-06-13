# fn-2-harden-acc-development-system.5 Fix post-audit setup drift

## Description
Post-audit setup drift fix after A-to-Z audit.

Scope:
- Re-patch installed Flow-Next hook cache so Windows cmd and PowerShell runs are clean.
- Refresh ACC installed cache verifier report from source.
- Document Windows PowerShell Flow-Next command usage in dev worktree docs.

No ACC plugin product feature work.
No GitHub push, PR update, merge, tag, publish, or release.
## Acceptance
- [ ] Flow-Next installed cache hooks exit 0 under cmd /c with empty stdout/stderr.
- [ ] Flow-Next installed cache hooks exit 0 under PowerShell with empty stdout/stderr.
- [ ] No-Ralph-file hook case exits 0 with empty stdout/stderr.
- [ ] Flow-Next hook JSON files parse and have no UTF-8 BOM.
- [ ] ACC installed cache VERIFIER-REPORT.json matches source.
- [ ] Flow validates after documentation/task updates.
- [ ] Product work remains paused pending user approval.
## Done summary
Fixed post-audit setup drift: re-patched installed Flow-Next hook cache with mechanically generated Windows-safe EncodedCommand, refreshed ACC runtime cache verifier report from source, and documented Windows PowerShell Flow-Next command usage in development docs. No ACC plugin product files changed and no GitHub action occurred.
## Evidence
- Commits:
- Tests:
- PRs: