---
name: usage
description: "Use when user asks token/cost/usage of Codex. Zero-token disk read; not for product features."
---

# Usage

See Codex usage and activity breakdown without spending any tokens.

Before large reads, broad searches, or loops, estimate context cost with
`scripts/work_visibility.py`. Always say usage estimates are approximate.
Compact tool output into receipts instead of pasting full logs into chat.

## Inline status (inside Codex, 0 tokens)

```
python scripts/codeburn.py status
```

Compact one-liner with today's sessions, tokens, and month total.
Zero tokens — reads session files directly from disk.

## Daily breakdown

```
python scripts/codeburn.py today
```

Today's sessions, by-model and by-activity breakdown with one-shot rate, top tools.

## Full report

```
python scripts/codeburn.py report            # last 7 days
python scripts/codeburn.py report -p 30d     # last 30 days
python scripts/codeburn.py report -p all     # entire history
python scripts/codeburn.py report --format json
```

## Web dashboard

```
python scripts/codeburn.py daemon
```

Starts web dashboard at http://localhost:8765.
Period tabs (Today/7d/30d/Month/All), model/activity/tool tables, daily trend chart.
Stop with `python scripts/codeburn.py stop`.

Background dashboard or scans must be visible, stoppable, bounded, and
receipt-producing. Do not leave indefinite hidden workers running.

## Export

```
python scripts/codeburn.py export              # JSON (7 days)
python scripts/codeburn.py export -f csv       # CSV
python scripts/codeburn.py export -p all       # full history
```

## When to use

- `$usage` for compact status check (0 tokens)
- `$usage` + `today` for daily review
- `$usage` + `daemon` for live web monitoring
- `$usage` + `report` for deep analysis

## When NOT to use

For Claude Code, Cursor, or other providers — use `npx codeburn`.

## Done — back to normal

When this skill's job is finished:
1. Stop following this skill.
2. Reply short and normal (caveman).
3. Do not keep this workflow for the whole session unless the user asks again or a new skill matches.
