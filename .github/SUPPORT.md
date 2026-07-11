# Support

Stuck? Use one of these:

| Need | Where |
|------|--------|
| Product site / install overview | [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) |
| Install / how-to | [README](../README.md) · [plugin README](../plugins/anyone-can-code/README.md) |
| Chat with people | [Discord](https://discord.gg/qgS29y7TqP) |
| Bug or idea | [GitHub Issues](https://github.com/mitunmanav/anyone-can-code/issues) |
| Soft questions | [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) |
| Security | [SECURITY.md](SECURITY.md) — **not** public issues |
| Docs map | [docs/README.md](../docs/README.md) |

Every issue gets an automatic **AI maintainer brief** (plain English) so the non-technical owner can act. Re-run with comment `/ai-review`.

## Before opening an issue

1. Read the [README](../README.md) install steps.
2. Run (remove secrets from output before sharing):

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
```

3. Include: OS, plugin version (Releases or `plugin.json`), what you ran, expected vs actual.

**Do not paste:** tokens, private paths, full memory notes, personal data.
