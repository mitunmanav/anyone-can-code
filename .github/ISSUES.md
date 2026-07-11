# Issues guide

Report problems so the maintainer (non-technical) and the AI brief can act.

## Pick a template

→ **[New issue](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)**

| Template | Use when |
|----------|----------|
| **Something is broken** | Crash, wrong result, weird failure |
| **Install / setup problem** | Marketplace, plugin install, or `$setup` failed |
| **Feature request** | Concrete change you want tracked |
| **Docs or website problem** | Wrong or confusing docs / site |
| **Technical contribution idea** | Engineer proposing a code change |

## Not an issue?

| Need | Go here |
|------|---------|
| How do I…? | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Q&A](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=q-a) |
| Soft brainstorm | [Ideas](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=ideas) |
| Live chat | [Discord](https://discord.gg/qgS29y7TqP) |
| Security | [Private advisory](https://github.com/mitunmanav/anyone-can-code/security/advisories/new) |

## Easy bug checklist

1. What you wanted  
2. What you did  
3. What happened (paste errors; strip secrets)  
4. Windows + Codex if you know them  
5. Optional doctor:

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
```

## What happens next

1. Issue is saved  
2. **AI issue review** posts a plain-English **Maintainer brief** (~1 min)  
3. Mitun reads the brief first  
4. Re-run AI: comment `/ai-review`

## Tips

- One problem per issue  
- Plain English beats perfect tech terms  
- Never paste tokens, passwords, or full memory files  

More: [SUPPORT.md](SUPPORT.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
