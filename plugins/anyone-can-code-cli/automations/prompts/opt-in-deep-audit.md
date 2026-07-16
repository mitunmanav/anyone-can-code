# Opt-in AI deep audit (permission first)

**[HUNGRY]** This spends tokens. OFF by default. Only schedule after the user
says YES in plain words.

## When to use

User asked for a deep audit, or agreed after: "Run a deep audit later on a
schedule? Costs tokens. YES / NO."

## Prompt to paste into Codex Scheduled

```
PERMISSION CHECK: Only continue if this project has an explicit user yes for
"deep audit automation". If unsure, archive with: "Deep audit skipped — no
permission on file."

If permitted: read .codex/anyone-can-code/state/ and recent memory notes.
Report max 8 bullets: real risks, weak tests, secrets smell, and one next fix.
Do NOT change code. Do NOT deploy. Read-only.
Speak caveman style: simple, short, direct, no ceremony.
If nothing important, archive with nothing to report.
```

## Schedule suggestion

Weekly is enough. Not daily unless the user asks.
