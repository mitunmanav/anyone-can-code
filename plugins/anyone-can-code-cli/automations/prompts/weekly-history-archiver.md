# Weekly History Archiver

**Schedule**: Weekly (Sunday, after Learning Pruner)
**Mode**: Workspace-write (new worktree)
**Model**: gpt-5.4-mini, reasoning: low

## Prompt to create the automation:

> Create a weekly automation that runs at 1:00am every Sunday. Use a new worktree for workspace-write operations. Each run:
> 1. Check .codex/anyone-can-code/state/workflow.json - if active session exists, postpone 24 hours.
> 2. Read .codex/anyone-can-code/logs/mistake-ledger.jsonl and signal-ledger.jsonl.
> 3. Move entries older than 90 days to .codex/anyone-can-code/artifacts/history/archived/{year-month}.md
> 4. Keep last 90 days in main files.
> 5. NEVER prune decisions, sessions, or changes ledgers unless user asks.
> 6. Report to Triage only if archival happened.
> 7. If nothing moved: archive silently. No user notification.
