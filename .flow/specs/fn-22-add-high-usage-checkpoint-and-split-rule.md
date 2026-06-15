# Add high usage checkpoint and split rule

## Problem

Raw session evidence showed primary usage rising from 85% to 94% with no ACC checkpoint, split, or stop. ACC already estimates large reads and loops, but it does not expose a hard high-usage session rule that prevents long work from burning the active chat.

## Requirements

- Treat 85% primary usage as checkpoint-required.
- Treat 90% primary usage as split-required before more work.
- Treat 94% primary usage as stop-now unless the user explicitly chooses to continue.
- Make the rule deterministic and testable in product code, not only prose.
- Surface the rule through front-door guidance, status/resume/verify/orchestrator docs, Doctor, and tests.
- Preserve uncertainty: token accounting can be approximate, so the rule uses reported percentage plus explicit uncertainty.

## Acceptance

- Unit tests prove 84% allows continuing, 85% requires checkpoint, 90% requires split, and 94% requires stop-now.
- Front-door route metadata exposes the usage checkpoint contract.
- Skill docs require ACC to checkpoint/split before high usage burns the session.
- Doctor reports the usage checkpoint rule as available.
- Existing usage-budget behavior remains intact.
- Flow validate, Doctor, compile, and relevant tests pass.
