# Issues guide

Report problems in a way the maintainer (non-technical) and the AI brief can act on.

## Pick the right template

Open → **[New issue](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)**

| Template | Use when |
|----------|----------|
| **Something is broken** | Crash, wrong result, weird failure |
| **Install / setup problem** | Marketplace, plugin install, or `$setup` failed |
| **Feature request** | You want a concrete change tracked |
| **Docs or website problem** | Wrong or confusing docs / site |
| **Technical contribution idea** | Engineer proposing a code change |

## Not an issue?

| Need | Go here |
|------|---------|
| How do I…? | [Discussions Q&A](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=q-a) · [FAQ #9](https://github.com/mitunmanav/anyone-can-code/discussions/9) |
| Soft brainstorm | [Discussions Ideas](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=ideas) |
| Live chat | [Discord](https://discord.gg/qgS29y7TqP) |
| Security | [Private advisory](https://github.com/mitunmanav/anyone-can-code/security/advisories/new) |
| Discussions map | [DISCUSSIONS.md](DISCUSSIONS.md) · [Start here #5](https://github.com/mitunmanav/anyone-can-code/discussions/5) |

## Easy bug checklist

1. Say **what you wanted**.  
2. Say **what you did**.  
3. Say **what happened** (paste errors; strip secrets).  
4. Add **Windows + Codex** if you know them.  
5. Optional: doctor output  

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
```

## What happens next

1. GitHub saves your issue.  
2. **AI issue review** posts a **Maintainer brief** in plain English (~1 minute).  
3. Mitun reads the brief first, then decides.  
4. Re-run AI: comment `/ai-review`.

## Tips

- One problem per issue.  
- Plain English beats perfect technical terms.  
- Never paste tokens, passwords, or full memory files.  
- Outside **AI coding agents** may be paused when maintainer focus is ON — humans can still open issues.

More: [SUPPORT.md](SUPPORT.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
