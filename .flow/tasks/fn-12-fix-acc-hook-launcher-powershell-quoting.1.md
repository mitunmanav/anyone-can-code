# fn-12-fix-acc-hook-launcher-powershell-quoting.1 Fix bundled hook launch under PowerShell outer shell

## Description
TBD

## Acceptance
- [ ] TBD

## Done summary
Replaced ACC bundled hook launchers with PowerShell EncodedCommand wrappers so outer PowerShell shells cannot strip dollar variables. Refreshed installed ACC hook files after backup at C:\tmp\acc-hook-powershell-quoting-before-20260614-192647. Added regression for PowerShell outer-shell launch.
## Evidence
- Commits:
- Tests: RED reproduced PowerShell outer-shell parser failure, Focused hook shell regressions: 3 OK, Installed cache 1.0.0 all six hook events pass under cmd and PowerShell outer shell, Installed cache 1.0.0+codex.20260613140139 all six hook events pass under cmd and PowerShell outer shell, python -m unittest discover plugins/anyone-can-code/tests: 91 OK, py_compile required hook and Doctor scripts: pass, Doctor: 33 PASS 0 WARN 0 FAIL, Flow validate all: valid, git diff --check: pass with line-ending warning only
- PRs: