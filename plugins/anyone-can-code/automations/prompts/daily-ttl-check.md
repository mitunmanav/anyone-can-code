# Daily TTL Cache Expiry Check

**Schedule**: Daily (runs when Codex app is open)
**Mode**: Read-only (local checkout)
**Model**: gpt-5.4-mini, reasoning: low

## Prompt to create the automation:

> Create a daily automation that runs at 8am local time. Use read-only mode on local checkout. Each run:
> 1. Check .codex/anyone-can-code/state/workflow.json - if active session exists, skip and archive silently.
> 2. Read all files in .codex/anyone-can-code/artifacts/search-results/.
> 3. For each file: compare expires field to today's date.
>    - If expired: set status to "expired", add to Triage report
>    - If stale (within 20% of TTL): set status to "stale" (no user notification)
>    - If fresh: no action
> 4. If any expired results: surface to Triage with one line per result: "[topic] searched on [date] has expired - re-search? (type: [type])"
> 5. If nothing expired: archive silently. No user notification.
