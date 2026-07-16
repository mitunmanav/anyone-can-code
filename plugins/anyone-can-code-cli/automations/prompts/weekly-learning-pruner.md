# Weekly Learning Pruner

**Schedule**: Weekly (Sunday midnight)
**Mode**: Workspace-write (new worktree)
**Model**: gpt-5.4-mini, reasoning: low

## Prompt to create the automation:

> Create a weekly automation that runs at 12:00am every Sunday. Use a new worktree for workspace-write operations. Each run:
> 1. Check .codex/anyone-can-code/state/workflow.json - if active session exists, postpone 24 hours.
> 2. Read .codex/anyone-can-code/learning/patterns.md and mistakes.md.
> 3. For each entry: check last_queried date.
>    - Not queried in 90+ days AND not marked as critical -> move to learning/archived/
>    - Queried recently -> keep in place
> 4. NEVER prune or touch .codex/anyone-can-code/learning/feedback.md (user corrections are permanent).
> 5. Count how many were pruned.
> 6. If pruned > 0: report to Triage: "Archived [N] stale learning entries."
> 7. If nothing pruned: archive silently. No user notification.
