# Anyone Can Code - Project Context

## Workflow Snapshot
- Phase: build
- Route: Flow-Next local development
- Entry mode: existing project
- Last task: `fn-12-fix-acc-hook-launcher-powershell-quoting.1` completed
- Current task: none; active captured follow-up is
  `fn-25-build-acc-core-everything-workflow-from`
- Communication mode: caveman-strict
- Development memory mode: Obsidian project brain first
- Product memory target: portable linked Markdown through bundled MCP, with JSONL as migration input only

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
- ACC is the product under development in the full
  `C:\Users\Mitun Manav G Y\Desktop\Plugin development` tree, not an active
  helper there.
- No ACC plugin runtime, ACC hooks, ACC MCP, or ACC skills may be used inside
  the Plugin development project. Treat any ACC runtime activity there as a
  bug.
- Parent project config and repo project config both disable only
  `anyone-can-code@anyone-can-code-marketplace` for this project; the parent
  `.codex\anyone-can-code-hooks.disabled` marker remains only as
  defense-in-depth.
- Do not disable all Codex hooks to achieve this. Non-plugin hooks and other
  non-ACC tools can still work. Do not remove or bypass the ACC marker unless
  the user explicitly reverses this decision.

## Current Goal
- Reliability line `fn-13` through `fn-24` is completed and verified locally.
- New real-use follow-up captured from the Zenfit ACC runtime trial:
  `fn-25-build-acc-core-everything-workflow-from`.
- `fn-25` is not started. It owns the product gap where ACC should absorb the
  Zenfit git-manager workaround into plugin-owned workflow, plus mandatory
  audit checklist use, canonical state updates, learning evidence, and
  compaction re-anchor.
- ACC remains disabled as helper inside this Plugin development project.

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
- Before memory/learning product work resumes, complete
  `fn-4-build-portable-markdown-memory`; task `fn-1...5` depends on it.
- Before local `main` receives candidate work, run
  `scripts\check-promotion-scope.ps1` with the appropriate policy. Stop if it
  reports `FAIL`.
- Use `Projects\Anyone Can Code\02 Current Status.md` for status overview.
- Use `Projects\Anyone Can Code\03 Timeline.md` for reconstructed past work.
- Linear is legacy only. Do not read, write, sync, or create Linear items.

<!-- BEGIN FLOW-NEXT -->
## Flow-Next

This project uses Flow-Next for task tracking. On Windows PowerShell, use
`python .flow\bin\flowctl.py ...`; `.flow/bin/flowctl` is a Bash wrapper and
can hang or print nothing in PowerShell. Use Flow-Next instead of markdown TODOs
or TodoWrite.

**Quick commands:**
```powershell
python .flow\bin\flowctl.py list                # List all specs + tasks
python .flow\bin\flowctl.py specs               # List all specs
python .flow\bin\flowctl.py tasks --spec fn-N   # List tasks for spec
python .flow\bin\flowctl.py ready --spec fn-N   # What's ready
python .flow\bin\flowctl.py show fn-N.M         # View task
python .flow\bin\flowctl.py start fn-N.M        # Claim task
python .flow\bin\flowctl.py done fn-N.M --summary-file s.md --evidence-json e.json
```

**Creating a spec** ("create a spec", "spec out X", "write a spec for X"):

Create one directly — do NOT use `$flow-next-plan` (that breaks specs into tasks). The canonical 7-section spec scaffold lives at `.flow/templates/spec.md` (copied here by `$flow-next-setup`) — read it for the section list, scope ownership, and `## Decision Context` H3 conditional. To customize the scaffold for this project, copy `.flow/templates/spec.md` to `<repo-root>/SPEC.md` and edit there — the discovery cascade prefers it (first match wins): `<repo_root>/SPEC.md` → `<repo_root>/spec.md` → `.flow/templates/spec.md` → bundled plugin template.

```powershell
python .flow\bin\flowctl.py spec create --title "Short title" --json
python .flow\bin\flowctl.py spec set-plan <spec-id> --file <path> --json
```

For multiline `set-plan`, write through PowerShell stdin or a temporary file,
then pass `--file <path>`.

```text
# Title

# ... fill the 7 canonical sections (see SPEC.md / .flow/templates/spec.md)
```

After creating a spec, choose next step:
- `$flow-next-plan <spec-id>` — research + break into tasks
- `$flow-next-interview <spec-id>` — deep Q&A to refine the spec

**Rules:**
- Use `python .flow\bin\flowctl.py` for ALL task tracking on Windows
- Do NOT create markdown TODOs or use TodoWrite
- Re-anchor (re-read spec + status) before every task

**Optional — codebase feature map:** `$flow-next-map` wraps [openclaw/clawpatch](https://github.com/openclaw/clawpatch)'s `clawpatch map` command to build a semantic feature index under `.clawpatch/features/*.json`. When present, `repo-scout` and `context-scout` use it to anchor R-IDs and `Investigation targets` to concrete codebase regions. Provider-free by default; install via `pnpm add -g clawpatch` (Node 22+).

**More info:** `python .flow\bin\flowctl.py --help` or read `.flow/usage.md`
<!-- END FLOW-NEXT -->
