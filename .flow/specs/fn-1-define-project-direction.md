# fn-1-define-project-direction Define project direction

## Goal & Context
<!-- scope: business -->

ACC is one front door for non-technical builders using Codex Windows Desktop.
The user describes what they want to build; ACC handles research, planning,
code, tests, Git, GitHub, portable Markdown learning, backend setup, and installed
skill/plugin routing. The user stays focused on product decisions, not tooling.

Primary persona: non-technical solo builder with no coding background. They do
not know or want to manage lint, type checks, pull requests, backend setup, or
deployment details. Developers are supported, but the default product behavior
optimizes for builders.

Persona is selected once during setup: builder, developer, or mixed. The rest of
ACC auto-configures from that choice.

First useful feature: product intake plus auto-engineering checklist. The user
can say "I want to build a website." ACC asks only the blocking questions needed
to proceed, generates an adapted engineering checklist, and shows one concise
plan line such as:

```text
Plan: website + auth + deploy. Payments later.
```

Nothing else takes priority until this intake-to-plan flow works.

## Architecture & Data Models
<!-- scope: technical -->

ACC should be built as a front-door orchestrator that works with Codex Desktop
instead of replacing it. It should bridge available installed skills/plugins
when relevant, while preserving a simple user-facing surface.

Core product modules:

- Intake engine: asks blocking questions and captures answers.
- Persona setup: stores builder/developer/mixed mode and configures defaults.
- Product classifier: maps request to product type such as website, app, game, API, script, automation, plugin, data tool, dashboard, native app, internal tool, or unknown.
- Checklist generator: produces adapted checklist across frontend, backend, DB, auth, payments, security, performance, SEO, analytics, deploy, tests, docs, UX theme, responsive behavior, accessibility, loading states, and error states.
- Skill/plugin bridge: routes to available skills/plugins automatically and returns to ACC if external workflow goes null or cannot continue.
- Observability line: reports exact state, failures, silent failures, and unverified work in user-readable form.
- Memory adapter: stores lessons in portable linked Markdown, retrieves top
  3-5 relevant memories, and treats memory as advisory rather than
  authoritative. Legacy JSONL remains migration input only until
  `fn-4-build-portable-markdown-memory` is complete.
- Git/GitHub adapter: handles commits, PRs, rollback, and project history.
- Scope controller: keeps plan cursor visible and prevents uncontrolled
  expansion.

Initial data shapes should stay small and explicit:

```text
PersonaConfig:
  mode: builder | developer | mixed
  verbosity: simple | technical
  automation_level: guided | assisted | autonomous

ProductIntake:
  product_type: website | app | api | game | plugin | automation | unknown
  goal: string
  target_user: string
  must_haves: string[]
  repo_mode: new | existing | unknown
  deadline: string | none | unknown

ChecklistItem:
  area: frontend | backend | db | auth | payments | security | seo | deploy | tests | docs
  decision: include | defer | skip | unknown
  reason: string
  state: in scope | designed | approved | implemented | verified | blocked | deferred

StatusLine:
  built_state: in scope | designed | approved | implemented | verified | blocked | deferred
  test_state: in scope | designed | approved | implemented | verified | blocked | deferred
  deploy_state: in scope | designed | approved | implemented | verified | blocked | deferred
  summary: string
```

## API Contracts
<!-- scope: technical -->

The first implementation should expose internal commands/functions equivalent
to these contracts. Exact filenames and UI surface can be decided during
planning.

```text
setupPersona(mode) -> PersonaConfig
```

Stores persona mode and configures default behavior.

```text
runProductIntake(initialRequest, existingContext?) -> ProductIntake
```

Asks at most five blocking questions:

1. What does it do?
2. Who uses it?
3. What are the must-haves?
4. New repo or existing repo?
5. Any deadline?

```text
generateEngineeringChecklist(intake, personaConfig) -> ChecklistItem[]
```

Adapts checklist to product type and marks each area include/defer/skip/unknown.

```text
renderPlanLine(intake, checklist) -> string
```

Returns one user-facing line, for example:

```text
Plan: website + auth + deploy. Payments later.
```

```text
renderStatusLine(states) -> string
```

Uses exact state vocabulary only: in scope, designed, approved, implemented, verified, blocked, deferred.
Example:

```text
Status: implemented, tests verified, deploy blocked
```

## Edge Cases & Constraints
<!-- scope: technical -->

- Windows Codex Desktop compatibility is mandatory.
- ACC must not fight the Codex app or hide important Codex safety prompts.
- User-facing copy must avoid developer jargon for builder persona.
- Installed skills/plugins may be missing; ACC must degrade cleanly.
- Memory can suggest, never decide truth.
- Checklist must adapt by product type and avoid one generic mega-list.
- Human-readable output matters: a developer should understand generated code
  and project structure within 10 minutes.
- Git/GitHub/PR/rollback should be automated only after safe project state is
  known.
- The development system used to build ACC must not leak into the shipped
  plugin UX.
- Self-learning, observability, model advice, and advanced automation are secondary until product intake plus checklist works, but their contracts must be represented in plan/state so later tasks do not drift. Durable self-learning implementation waits for `fn-4-build-portable-markdown-memory`.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** A builder can start from a plain-language request such as "I want to
  build a website" and ACC begins product intake.
- **R2:** Product intake asks no more than five blocking questions: what it does,
  who uses it, must-haves, new/existing repo, and deadline.
- **R3:** ACC generates a checklist adapted to product type, covering relevant
  frontend, backend, DB, auth, payments, security, SEO, deploy, tests, and docs
  decisions.
- **R4:** ACC renders a concise plan line such as `Plan: website + auth +
  deploy. Payments later.`
- **R5:** Persona setup supports builder, developer, and mixed modes, and stores
  the chosen mode for later behavior.
- **R6:** ACC can route to installed skills/plugins automatically when they are
  relevant and available.
- **R7:** ACC renders observability using exact states: in scope, designed, approved, implemented, verified, blocked, deferred.
- **R8:** Git/GitHub/PR handling has rollback support before being treated as
  complete.
- **R9:** Self-learning stores lessons in portable linked Markdown, recalls the
  top 3-5 relevant lessons, and never treats memory as truth.
- **R10:** Generated code and project output remain human-readable enough for a
  developer to understand within 10 minutes.
- **R11:** The plugin works on Windows Codex Desktop without conflicting with
  Codex app workflows.
- **R12:** Dev-system concepts used to build ACC do not appear in the shipped
  user-facing plugin flow.
- **R13:** Caveman communication is default across every user-facing skill and can be switched by explicit setting.
- **R14:** ACC handles product types: website, app, game, API, script, automation, plugin, data tool, dashboard, and native app.
- **R15:** ACC handles UX checklist decisions for theme, responsive behavior, accessibility, loading states, error states, and performance.
- **R16:** During ACC development, the agent reads official/local docs before execution and uses web only when local docs are stale, missing, or uncertain. This is a development-process rule, not shipped plugin UX.
- **R17:** ACC owns setup, installs, environments, local servers, DB, auth, payments, deployment, Git, GitHub, PRs, CI, branches, and commits, asking users only for secrets, paid service choices, account logins, destructive actions, and product decisions.
- **R18:** ACC backs up or creates rollback path before risky changes.
- **R19:** ACC learns from sessions across project, user, and shared scopes,
  including user-supplied existing local session files and model/task fit from
  local session evidence.
- **R20:** ACC reports what happened, what failed, what failed silently, and what remains unverified; it never says done without verification.
- **R21:** ACC captures mid-work requirement changes, updates plan/state, and resumes from the correct task position.
- **R22:** ACC settings cover tone, depth, research, learning, approvals, and plugin routing with automatic defaults.
- **R23:** ACC treats new projects, existing projects, and production repos differently; production repos use stricter caution.
- **R24:** ACC uses subagents for parallel reading/research when available and valuable.
- **R25:** ACC can search web when doubt remains after local context and surfaces missing requirements instead of ignoring them.

## Boundaries
<!-- scope: business -->

In scope for first useful feature:

- Product intake.
- Persona setup basics.
- Product-type classification.
- Adaptive engineering checklist.
- One-line plan output.
- Initial observability line vocabulary.
- Skill/plugin bridge design enough to route later.

Out of scope until intake works:

- Full autonomous Ralph loop for end users.
- Advanced self-learning UX.
- Full portable Markdown memory migration and existing-session import; this is
  owned by `fn-4-build-portable-markdown-memory`.
- Model advice line.
- Full deploy automation.
- Full GitHub PR automation implementation.
- Complete rollback implementation.
- Broad observability dashboards.
- Payment integration beyond checklist decisioning.

Hard product boundary:

The development system is not the shipped product. Candidate/stable workflow,
inspiration audit ledger, docs citation audit, spec gates, reversible promotion,
build validation, Doctor, implementation logs, hook proof journal, and phase
gates are only for safely building ACC. They must not be exposed as the user
experience.

## Decision Context
<!-- scope: both -->

### Motivation
<!-- scope: business -->

Non-technical builders need a product front door, not a tooling dashboard. The
first value is reducing "I want to build X" into a clear, scoped plan without
requiring the user to understand engineering process. ACC should make Codex
Desktop feel like a product-building environment rather than a collection of
separate tools.

### Implementation Tradeoffs
<!-- scope: technical -->

The first slice should prefer deterministic intake and checklist generation over
deep automation. That gives a testable foundation and avoids building autonomous
systems before ACC knows what product is being built. Skill/plugin bridging
should be routed through explicit availability checks, not assumptions. Memory
should be useful context, but never source of truth. Git/GitHub automation and
Ralph can build on this later after plan generation is reliable.

### Post-Obsidian Repair Checkpoint
<!-- scope: both -->

Tasks `.1` through `.4` remain valid because they built persona setup, intake,
routing, plugin bridge, and exact status language. They did not finish durable
learning. Any surface from those tasks that mentions bundled MCP/JSONL memory
must be updated by `fn-4-build-portable-markdown-memory.4` before task `.5`
starts. Task `.5` is blocked by the spec-level dependency on `fn-4`.

## Quick commands
<!-- scope: technical -->

```powershell
python plugins/anyone-can-code/scripts/doctor.py --json
python -m py_compile plugins/anyone-can-code/mcp/server.py plugins/anyone-can-code/scripts/setup.py plugins/anyone-can-code/scripts/doctor.py
python .flow/bin/flowctl.py validate --spec fn-1-define-project-direction --json
```

## Early proof point
<!-- scope: both -->

Task `fn-1-define-project-direction.2` proves the core approach: a plain-language product request can become bounded intake, an adaptive checklist, and a concise builder-readable plan line. If it fails, reconsider ACC's front-door strategy before expanding routing, GitHub, learning, or Ralph automation.

## Requirement coverage
<!-- scope: both -->

| Req | Description | Task(s) | Gap justification |
|-----|-------------|---------|-------------------|
| R1 | Builder starts from plain-language request and intake begins | fn-1-define-project-direction.2, fn-1-define-project-direction.3 | - |
| R2 | Intake asks no more than five blocking questions | fn-1-define-project-direction.2 | - |
| R3 | Checklist adapts by product type | fn-1-define-project-direction.2 | - |
| R4 | Concise plan line renders | fn-1-define-project-direction.2 | - |
| R5 | Persona setup supports builder/developer/mixed | fn-1-define-project-direction.1 | - |
| R6 | Installed skills/plugins route automatically when relevant | fn-1-define-project-direction.3 | - |
| R7 | Observability line uses exact states | fn-1-define-project-direction.4 | - |
| R8 | Git/GitHub/PR handling has rollback support | fn-1-define-project-direction.5 | First spec builds guardrails/scaffold; full automation remains out of scope until intake works. |
| R9 | Self-learning stores linked Markdown lessons and recalls top 3-5 lessons without treating memory as truth | fn-4-build-portable-markdown-memory, fn-1-define-project-direction.5 | fn-4 changes durable storage first; `.5` adds final guardrail UX after migration. |
| R10 | Output remains human-readable within 10 minutes | fn-1-define-project-direction.4, fn-1-define-project-direction.5 | - |
| R11 | Windows Codex Desktop compatible | fn-1-define-project-direction.1, fn-1-define-project-direction.4 | - |
| R12 | Dev-system concepts do not leak into shipped UX | fn-1-define-project-direction.3, fn-1-define-project-direction.5 | - |
| R13 | Caveman default everywhere, switchable | fn-1-define-project-direction.1, fn-1-define-project-direction.4 | - |
| R14 | Broad product type support | fn-1-define-project-direction.2 | - |
| R15 | UX checklist coverage | fn-1-define-project-direction.2, fn-1-define-project-direction.4 | - |
| R16 | Development-process docs rule, not shipped plugin UX | fn-2-harden-acc-development-system, AGENTS.md, DEVELOPMENT-WORKFLOW.md | User clarified R16 belongs to ACC development system only. |
| R17 | Tooling/Git/env ownership with narrow user asks | fn-1-define-project-direction.5 | Full automation staged after intake works; guardrail contract lands now. |
| R18 | Backup/rollback before risky changes | fn-1-define-project-direction.5 | - |
| R19 | Session learning, existing local session import, and model/task fit memory | fn-4-build-portable-markdown-memory, fn-1-define-project-direction.5 | fn-4 owns Markdown storage/import; `.5` owns final learning guardrails. |
| R20 | Failure/silent failure/unverified reporting; no false done | fn-1-define-project-direction.4 | - |
| R21 | Requirement-change capture and resume | fn-1-define-project-direction.3, fn-1-define-project-direction.4, fn-1-define-project-direction.5 | `.3`/`.4` define route/status; `.5` must preserve cursor during learning/Git guardrails. |
| R22 | Settings with automatic defaults, including memory path/viewer/import choices | fn-1-define-project-direction.1, fn-4-build-portable-markdown-memory | fn-4 adds memory-specific settings. |
| R23 | New/existing/production repo modes, including session import caution | fn-1-define-project-direction.1, fn-1-define-project-direction.2, fn-4-build-portable-markdown-memory | fn-4 adds memory/session import behavior per repo mode. |
| R24 | Efficient subagent use | fn-1-define-project-direction.3 | - |
| R25 | Web search on doubt and missing requirement surfacing | fn-1-define-project-direction.3, fn-1-define-project-direction.5 | - |

## References
<!-- scope: technical -->

- `plugins/anyone-can-code/README.md` - current plugin workflow and data layout.
- `plugins/anyone-can-code/IMPLEMENTATION-SOURCE-OF-TRUTH.md` - reused/refactored/removed/added boundaries.
- `plugins/anyone-can-code/scripts/setup.py` - project bootstrap and preferences.
- `plugins/anyone-can-code/scripts/doctor.py` - diagnostics and validation entry point.
- `plugins/anyone-can-code/mcp/server.py` - MCP-first memory implementation.
- `plugins/anyone-can-code/skills/orchestrator/SKILL.md` - front-door routing surface.
- `plugins/anyone-can-code/skills/clarify/SKILL.md` - intake surface.
- `plugins/anyone-can-code/skills/bridge/SKILL.md` - installed plugin routing.
- `plugins/anyone-can-code/skills/verify/SKILL.md` - evidence-first verification.
