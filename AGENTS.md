# Anyone Can Code - Project Context

## Workflow Snapshot
- Phase: build
- Route: Flow-Next local development
- Entry mode: existing project
- Last task: `fn-2-harden-acc-development-system` spec created
- Next task: `fn-2-harden-acc-development-system.1` define change-impact matrix
- Communication mode: caveman-strict
- Memory mode: mcp-first

## Expectations
- User-visible replies must use caveman-full style across this project at all times.
- Keep technical terms exact, but drop filler and keep output terse.
- Only stop caveman style when user says `stop caveman` or `normal mode`.
- This project uses an evidence-first workflow.
- High-impact uncertainty should pause and ask.
- Verification happens before completion claims.
- Local state lives under `.codex/anyone-can-code/`.
- While developing ACC itself, use Obsidian MCP first for project/docs memory. Read `official-codex-docs/index` in the vault before relying on web docs. If those docs are stale, missing, or contradict current behavior, verify with web search and record the reason.
- Inspiration repos are allowed for ACC plugin architecture and AI-agent workflow ideas. Clone them under `C:\Users\Mitun Manav G Y\Desktop\Plugin development\inspiration`.
- Use codegraph MCP to index and read inspiration/codebase structure efficiently. For files not covered by codegraph, read only targeted files with `rg`/direct file reads.
- Do not dump whole repos, whole docs folders, or large raw files into context. Summarize findings, cite paths, and pull only the slices needed for the current task.
- When anything changes, automatically update every affected repo doc, Flow record, and Obsidian note required to keep truth current.
- Record agent actions, decisions, what happened, what did not happen, evidence, warnings, and next state into Obsidian immediately during the work, not later.

## Current Goal
- Harden the ACC development system around Flow-Next before resuming plugin
  product task `fn-1-define-project-direction.3`.

## Project Delivery Model
- Obsidian is the complete project brain and history: requests, decisions, explanations, evidence, reversals, and continuity.
- Obsidian vault home: `I:\Obsidian vaults\Projects\Anyone Can Code\00 ACC Home.md`.
- Flow-Next is local source of truth for technical specs, engineering tasks, dependencies, and task evidence.
- Chat requirement changes must be captured in Obsidian first, then reconciled into Flow when they affect technical work.
- Linear is not the active product tracker unless the user explicitly re-enables it.
- Development happens only in `.worktrees/dev-*`.
- Candidate validation happens in `.worktrees/test-candidate`; no feature implementation there.
- Root `main` checkout is approved clean code.
- Online GitHub `main` must be an exact copy of local `main`, updated only after the user explicitly commands a push.
- Do not push development branches unless the user explicitly commands that exact action.
- Keep `test-candidate` local-only.
- Publish/release only from approved local `main`.
- Follow `DEVELOPMENT-WORKFLOW.md`.
- Before plugin-product work resumes, complete the development reliability gate
  in `fn-2-harden-acc-development-system`.
- Before local `main` receives candidate work, run
  `scripts\check-promotion-scope.ps1` with the appropriate policy. Stop if it
  reports `FAIL`.
- Use `Projects\Anyone Can Code\02 Current Status.md` for status overview.
- Use `Projects\Anyone Can Code\03 Timeline.md` for reconstructed past work.
- Linear is legacy only. Do not read, write, sync, or create Linear items.

<!-- BEGIN FLOW-NEXT -->
## Flow-Next

This project uses Flow-Next for task tracking. Use `.flow/bin/flowctl` instead of markdown TODOs or TodoWrite.

**Quick commands:**
```bash
.flow/bin/flowctl list                # List all specs + tasks
.flow/bin/flowctl specs               # List all specs
.flow/bin/flowctl tasks --spec fn-N   # List tasks for spec
.flow/bin/flowctl ready --spec fn-N   # What's ready
.flow/bin/flowctl show fn-N.M         # View task
.flow/bin/flowctl start fn-N.M        # Claim task
.flow/bin/flowctl done fn-N.M --summary-file s.md --evidence-json e.json
```

**Creating a spec** ("create a spec", "spec out X", "write a spec for X"):

Create one directly — do NOT use `$flow-next-plan` (that breaks specs into tasks). The canonical 7-section spec scaffold lives at `.flow/templates/spec.md` (copied here by `$flow-next-setup`) — read it for the section list, scope ownership, and `## Decision Context` H3 conditional. To customize the scaffold for this project, copy `.flow/templates/spec.md` to `<repo-root>/SPEC.md` and edit there — the discovery cascade prefers it (first match wins): `<repo_root>/SPEC.md` → `<repo_root>/spec.md` → `.flow/templates/spec.md` → bundled plugin template.

```bash
.flow/bin/flowctl spec create --title "Short title" --json
.flow/bin/flowctl spec set-plan <spec-id> --file - --json <<'EOF'
# Title

# ... fill the 7 canonical sections (see SPEC.md / .flow/templates/spec.md)
EOF
```

After creating a spec, choose next step:
- `$flow-next-plan <spec-id>` — research + break into tasks
- `$flow-next-interview <spec-id>` — deep Q&A to refine the spec

**Rules:**
- Use `.flow/bin/flowctl` for ALL task tracking
- Do NOT create markdown TODOs or use TodoWrite
- Re-anchor (re-read spec + status) before every task

**Optional — codebase feature map:** `$flow-next-map` wraps [openclaw/clawpatch](https://github.com/openclaw/clawpatch)'s `clawpatch map` command to build a semantic feature index under `.clawpatch/features/*.json`. When present, `repo-scout` and `context-scout` use it to anchor R-IDs and `Investigation targets` to concrete codebase regions. Provider-free by default; install via `pnpm add -g clawpatch` (Node 22+).

**More info:** `.flow/bin/flowctl --help` or read `.flow/usage.md`
<!-- END FLOW-NEXT -->
