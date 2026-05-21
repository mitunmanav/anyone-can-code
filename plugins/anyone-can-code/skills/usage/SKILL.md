---
name: usage
description: "Shows Codex token usage, activity breakdown, and tool patterns — zero tokens spent. Runs codeburn.py for compact inline status or web dashboard. Reads session files from disk, no API calls."
---

# Usage

See Codex usage and activity breakdown without spending any tokens.

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
