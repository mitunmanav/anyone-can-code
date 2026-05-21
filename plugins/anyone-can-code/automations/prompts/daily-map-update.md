# Daily Codebase Map Update

**Schedule**: Daily
**Mode**: Workspace-write (new worktree)
**Model**: gpt-5.4-mini, reasoning: low

## Prompt to create the automation:

> Create a daily automation that runs at 9am local time. Use a new worktree for workspace-write operations. Each run:
> 1. Check .codex/anyone-can-code/state/workflow.json - if active session exists, skip and archive silently.
> 2. Run: git diff --name-only HEAD~1 HEAD
> 3. For each changed file: read file, update its entry in .codex/anyone-can-code/artifacts/codebase-map.md (area tags, one-line purpose)
> 4. For deleted files: remove entry from map
> 5. For new files: add entry with tags
> 6. Commit change to codebase-map.md with message: "chore: update codebase map [date]"
> 7. If no changes since last run: archive silently. No user notification.
