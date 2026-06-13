# fn-3-automate-safe-local-promotion.2 Allow Flow usage docs in setup promotion guard

## Description
﻿Root cause: setup-fix promotion changed `.flow/usage.md`, but every guard policy rejected that file. The guard blocked a valid development-system documentation promotion.

Work: update promotion guard tests and policy so scoped setup/reliability promotions may include `.flow/usage.md` without opening plugin product files.
## Acceptance
﻿- [ ] Test proves reliability policy allows `.flow/usage.md`.
- [ ] Guard still blocks plugin product drift under reliability policy.
- [ ] Guard tests pass.
- [ ] Setup-fix commit can pass guard when checked as a single commit.
## Done summary
Allowed .flow/usage.md in safe promotion guard for reliability/docs-only policies. Added regression test. Verified setup-fix commit now passes reliability guard while old bad development delta still fails and lists forbidden product files.
## Evidence
- Commits:
- Tests: python -m unittest tests.test_check_promotion_scope, powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check-promotion-scope.ps1 -Base 85f367b^ -Candidate 85f367b -Policy reliability, powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check-promotion-scope.ps1 -Base 79216cd -Candidate 7994630 -Policy reliability
- PRs: