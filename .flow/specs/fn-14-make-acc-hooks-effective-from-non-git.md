# fn-14 Make ACC hooks effective from non-Git workspace roots

## Goal & Context
<!-- scope: business -->

ACC hooks may be launched by Codex Desktop while producing no useful behavior.
The audited `website portfolios` session started from a non-Git workspace root,
while the active Git project and ACC state lived in nested `zenfit-site`.
Current hook scripts call `git rev-parse --show-toplevel` from hook process cwd
and return `{}` when that lookup fails. This prevents context injection, state
writes, health records, signal capture, memory work, and session saving.

Codex rollout JSONL cannot be the hook execution ledger. In Codex Desktop
`0.140.0-alpha.2`, `HookStarted`, `HookCompleted`, and warning events are
explicitly excluded from rollout persistence. Hook `additionalContext` can
persist only as an ordinary developer message without hook origin.

Official Codex research found two stronger future telemetry evidence paths:

- live app-server `hook/started` and `hook/completed` notifications;
- OpenTelemetry metrics `codex.hooks.run` and
  `codex.hooks.run.duration_ms`.

Neither replaces ACC-owned useful-effect proof. The current repair implements
the ACC-owned resolver, useful-output proof, state-write proof, and durable
receipts. Live app-server and OTLP capture remain optional future telemetry
work unless the user explicitly requests that separate platform harness.

## Architecture & Data Models
<!-- scope: technical -->

Add deterministic project-root discovery shared by all ACC hook scripts.
Discovery must support a non-Git workspace root containing one active nested ACC
project. It must not silently choose between multiple plausible nested projects.

Keep three evidence layers distinct:

1. Codex live app-server notifications when a controlled test harness can
   subscribe. `HookRunSummary` contains run ID, event, source path, source,
   status, status message, start/completion timestamps, duration, and output
   entries.
2. Official local OTLP metrics export for durable Codex-level counts and
   durations. Metrics identify hook event, source, status, and duration.
3. ACC append-only per-hook receipts for project resolution, returned useful
   context/output, state mutation, skip reason, and internal effectiveness.

Live notifications are transient and thread reconstruction ignores them.
Metrics are coarse and do not identify plugin path, internal project discovery,
returned useful context, or state writes. ACC receipts remain required and are
the required evidence for this repair.

Each ACC attempt needs one correlation ID spanning launcher, script entry,
project resolution, useful output, state mutation, and completion. Receipts must
survive project-resolution failure through a bounded workspace fallback.

Minimum ACC receipt fields:

- schema version, correlation ID, session ID, turn ID, hook event, source;
- launcher start, script-entry time, completion time, duration;
- cwd, resolver candidates, chosen project, resolution state;
- output kind, redacted output digest, context-returned flag;
- state-write result and redacted written paths;
- skipped reason, failure class, exit status, circuit state;
- final effectiveness: `useful`, `no-op`, `skipped`, `failed`, or `blocked`.

## API Contracts
<!-- scope: technical -->

Hook scripts keep valid Codex hook JSON output. Successful context-producing
hooks return `hookSpecificOutput` with correct event name and useful
`additionalContext`. No-op or unresolved-project results remain safe but write
an inspectable reason. Receipt content must redact secrets and private prompt
content; store digests and bounded summaries instead of raw sensitive payloads.

Observability setup must be optional and consent-based. ACC must not silently
enable telemetry, start a collector, expose a listener, or transmit metrics.
Local OTLP collection must use an explicit local endpoint and documented
retention.

## Edge Cases & Constraints
<!-- scope: technical -->

- Workspace root is not a Git repository.
- One nested Git/ACC project exists.
- Multiple nested ACC projects exist.
- No Git or ACC project exists.
- Session cwd remains workspace root while tool calls target nested directories.
- Hook launcher exits zero but script returns `{}`.
- Launcher starts but script never enters.
- Script enters but cannot create project-local evidence.
- Process terminates before normal completion.
- Duplicate/retried delivery uses same or linked correlation IDs.
- App-server notification subscriber is absent or disconnected.
- OTLP collector is absent, unreachable, or disabled.
- Metrics show `source=plugin` but multiple plugins are enabled.
- ACC core operation must still work when hooks or observability are absent.
- Do not depend on rollout hook rows, private analytics, or remote telemetry.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** SessionStart and UserPromptSubmit can resolve intended nested ACC project from a non-Git workspace root without guessing across ambiguous candidates.
- **R2:** Resolved SessionStart output injects canonical state, next action, communication mode, memory mode, and project rules.
- **R3:** Resolved UserPromptSubmit output injects route and communication context and writes canonical transaction expected by hook contract.
- **R4:** Stop writes declared session-state outputs only to resolved project and never overwrites `AGENTS.md`.
- **R5:** Every attempted ACC hook has one durable correlated receipt proving launcher start, script entry, project resolution, returned context/output, state writes, skip/failure reason, exit status, duration, circuit state, and final effectiveness.
- **R6:** Receipt exists even when no project resolves, using bounded workspace fallback evidence without selecting arbitrary nested project.
- **R7:** Installed-runtime tests cover non-Git root plus nested project under both `cmd.exe` and PowerShell launch.
- **R8:** Exact output and file-write assertions prove hooks did useful work; exit code zero, UI completion, or telemetry count alone cannot pass.
- **R9:** Empty `{}` output is classified as `no-op` or `skipped` with reason, never `useful`.
- **R10:** Ambiguous nested projects produce safe unresolved result and plain recovery evidence instead of arbitrary selection.
- **R11:** Receipts redact raw prompts, secrets, tokens, and sensitive output while retaining hashes, bounded summaries, and correlation.
- **R12:** Doctor summarizes latest ACC receipts and distinguishes scheduler/launcher unknown, launcher-only, script-entered, unresolved, useful, skipped, failed, and circuit-open states.
- **R13:** Live app-server hook notification capture is recorded as a separate optional future telemetry proof layer, not a blocker for ACC-owned resolver/receipt repair.
- **R14:** Optional local OTLP hook metrics capture is recorded as a separate consented future telemetry proof layer, not a blocker for ACC-owned resolver/receipt repair.
- **R15:** Evidence comparison must never merge UI/live events, OTLP metrics, and ACC receipts into one false pass.
- **R16:** ACC works normally when live-event capture and OTLP collection are unavailable.

## Boundaries
<!-- scope: business -->

This spec captures audit-derived repair and observability boundaries. It does
not run ACC hooks inside Plugin development, run Session Analyzer, attach to
private Desktop internals, enable telemetry without consent, or change GitHub.
Future app-server/OTLP telemetry harness work requires explicit user approval.

## Decision Context
<!-- scope: both -->

### Motivation
<!-- scope: business -->

User observed hooks running. Exact-version source proves live hook lifecycle
events are not durable rollout records. Thorough official research found usable
live app-server notifications and supported OTLP metrics, but neither proves
ACC useful impact alone. ACC needs combined official runtime evidence and
privacy-safe internal receipts.

### Implementation Tradeoffs
<!-- scope: technical -->

App-server notifications provide richest Codex-level data but are transient and
require a subscribing client during execution. OTLP metrics are durable when a
collector is configured but aggregate away handler identity and useful output.
ACC receipts prove internal effects but cannot prove Codex attempted launch if
the wrapper never starts. Combining all three gives strongest available proof
without private APIs.
