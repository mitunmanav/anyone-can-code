# Fix ACC hook launcher PowerShell quoting

## Goal & Context

Codex Desktop showed hook exit-code failures again in the Plugin development project. Investigation found ACC bundled hook launch commands used inline PowerShell with `$` variables inside a command string. When Codex or tests launch that command through an outer PowerShell shell, the outer shell expands and strips those variables before the inner hook command runs. This can produce parser errors and exit code 1.

ACC is still the product here, not an active helper. The fix changes ACC source hook launcher definitions, refreshed installed hook files after backup, and local evidence records. No GitHub, push, PR, tag, release, or remote branch action.

## Requirements

- R1: ACC bundled hook commands survive `cmd.exe /c` launch.
- R2: ACC bundled hook commands survive PowerShell outer-shell launch.
- R3: Below the Plugin development ACC-disable marker, installed hooks exit 0 and output `{}` without state writes.
- R4: Installed cache hook files are refreshed only after backup.
- R5: Flow and Obsidian record the root cause, fix, verification, and remaining restart requirement.

## Plan

1. Add RED regression for PowerShell outer-shell hook launch.
2. Replace inline `-Command` hook launchers with `-EncodedCommand` launchers.
3. Refresh installed ACC hook files after backup.
4. Verify focused regression, full plugin tests, installed hook launch paths, Doctor, Flow validation, and diff check.

## Acceptance Checks

- Focused PowerShell outer-shell regression passes.
- Existing cmd and marketplace-root hook regressions pass.
- Installed `1.0.0` and `1.0.0+codex.20260613140139` hook files pass all events under cmd and PowerShell outer-shell launch.
- Full unittest suite passes.
- Doctor reports pass with no warnings or failures.
- Flow validation passes.
- No GitHub action occurs.
