# Daily AGENTS.md Health Check

**Schedule**: Daily
**Mode**: Workspace-write (new worktree)
**Model**: gpt-5.4-mini, reasoning: low

## Prompt to create the automation:

> Create a daily automation that runs at 10am local time. Use a new worktree for workspace-write operations. Each run:
> 1. Check .codex/anyone-can-code/state/workflow.json - if active session exists, skip and archive silently.
> 2. Read AGENTS.md at repo root.
> 3. Check byte size. If over 28KB (safe margin below 32KB combined limit):
>    - Compress lowest-priority sections (environment, old task details)
>    - Move compressed content to .codex/anyone-can-code/state/state-current.md overflow section
>    - Rewrite AGENTS.md within limit
>    - Report to Triage: "AGENTS.md compressed - [what was moved]"
> 4. Check that state, active task, and conventions sections are present.
> 5. If any missing: flag to Triage.
> 6. If all healthy: archive silently. No user notification.
