# Require reread after failed patch attempts

## Problem

Manual audit found repeated failed patch attempts. ACC guidance does not have a hard retry discipline that forces rereading the exact target after a patch miss.

## Requirements

- Add a deterministic patch-retry policy in product code.
- After any patch mismatch, stale context, or failed edit, require rereading the exact target block before retrying.
- Limit retry attempts so loops do not continue on stale context.
- Surface the policy through front-door route metadata and relevant skill docs.
- Make the rule testable and visible in Doctor smoke evidence.

## Acceptance

- Unit tests prove first attempt can proceed, a failed patch blocks retry until reread, reread allows one retry, and max retry exhaustion blocks.
- Front-door route metadata exposes the patch retry policy.
- Orchestrator/execute/status/verify docs require reread-before-retry.
- Doctor reports the policy as available.
- Flow validate, Doctor, compile, and relevant tests pass.
