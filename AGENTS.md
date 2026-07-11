# Anyone Can Code - Project Context

## Workflow Snapshot
- Phase: build / polish
- Route: local development, Obsidian-tracked
- Entry mode: existing project
- Current task: none; **v1.1.0-beta.3** is latest prerelease (fix-round). Public site live at https://anyone-can-code.vercel.app/
- Install (primary): Codex Plugins → Add marketplace with repo URL → Install ACC → **trust all hooks** → restart → `$setup`. Terminal marketplace add is optional only.
- Communication mode: caveman-strict

## User preferences (public product docs — do not regress)
- README: **short, clear, pitch-like** (not long essay). GIF in README; MP4 optional download.
- Non-technical first. Mitun voice OK if concise. No engineering-first framing.
- Native Codex from official docs — **not** migrated from other AI coding agents.
- Hooks trust is mandatory and must stay loud in install docs.
- Small polish only on site/docs — never redesign; never re-clutter with link walls.
- Development memory mode: Obsidian project brain first
- Product memory target: portable linked Markdown through bundled MCP, with JSONL as migration input only
- Docs map: `docs/README.md` (historical handoffs/plans are not current truth)

## Expectations
- User-visible replies must use caveman-full style across this project at all times.
- Keep technical terms exact, but drop filler and keep output terse.
- Only stop caveman style when user says `stop caveman` or `normal mode`.
- This project uses an evidence-first workflow.
- High-impact uncertainty should pause and ask.
- Verification happens before completion claims.
- Local state lives under `.codex/anyone-can-code/`.
- While developing ACC itself, read vault docs via `rtk read` / `rtk grep` on the mounted vault path (`/mnt/i/Obsidian vaults/...` in WSL) — never via Obsidian MCP reads (raw full text, wastes tokens). Obsidian MCP is for writes only. Read vault root `offical-codex-docs/index.md` (note typo spelling "offical") before relying on web docs. If those docs are stale, missing, or contradict current behavior, verify with web search and record the reason.
- Inspiration repos are allowed for ACC plugin architecture and AI-agent workflow ideas. Clone them under `C:\Users\<user>\Desktop\Plugin development\inspiration`.
- Use codegraph MCP to index and read inspiration/codebase structure efficiently. For files not covered by codegraph, read only targeted files with `rg`/direct file reads.
- Do not dump whole repos, whole docs folders, or large raw files into context. Summarize findings, cite paths, and pull only the slices needed for the current task.
- When anything changes, automatically update every affected repo doc and Obsidian note required to keep truth current.
- Record agent actions, decisions, what happened, what did not happen, evidence, warnings, and next state into Obsidian immediately during the work, not later.
- ACC is the product under development in the full
  `C:\Users\<user>\Desktop\Plugin development` tree, not an active
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
- v1.1.0-beta.3 released (prerelease). Product GitHub + website + community/CI
  setup in place (AI issue/PR briefs, agent guard, Validate CI).
- Next direction: real user trials toward a stable 1.1.0; keep docs accurate;
  one-line install + guided setup modes still on the roadmap.
- ACC remains disabled as helper inside this Plugin development project.

## Project Delivery Model
- Obsidian is the complete project brain and history: requests, decisions, explanations, evidence, reversals, and continuity.
- Obsidian vault home: `I:\Obsidian vaults\Projects\Anyone Can Code\00 ACC Home.md`.
- Chat requirement changes must be captured in Obsidian first, with technical detail kept current there too.
- Linear is not the active product tracker unless the user explicitly re-enables it.
- Development happens only in `.worktrees/dev-*`.
- Candidate validation happens in `.worktrees/test-candidate`; no feature implementation there.
- Root `main` checkout is approved clean code.
- Online GitHub `main` must be an exact copy of local `main`, updated only after the user explicitly commands a push.
- Do not push development branches unless the user explicitly commands that exact action.
- Keep `test-candidate` local-only.
- Publish/release only from approved local `main`.
- Follow `DEVELOPMENT-WORKFLOW.md`.
- Before local `main` receives candidate work, run
  `scripts\check-promotion-scope.ps1` with the appropriate policy. Stop if it
  reports `FAIL`.
- Use `Projects\Anyone Can Code\02 Current Status.md` for status overview.
- Use `Projects\Anyone Can Code\03 Timeline.md` for reconstructed past work.
- Linear is legacy only. Do not read, write, sync, or create Linear items.

