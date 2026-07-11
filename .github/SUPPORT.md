# Support

Stuck? Pick the **smallest** path that fits.

## Where to go

| Need | Where |
|------|--------|
| Install overview | [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) |
| Install steps | [README](../README.md) · [plugin README](../plugins/anyone-can-code/README.md) |
| How-to question | [Discussions → Q&A](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=q-a) |
| Soft idea | [Discussions → Ideas](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=ideas) |
| Show what you built | [Discussions → Show and tell](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=show-and-tell) |
| Full Discussions map | [DISCUSSIONS.md](DISCUSSIONS.md) |
| Live chat | [Discord](https://discord.gg/qgS29y7TqP) |
| Bug / crash | [GitHub Issues — Bug](https://github.com/mitunmanav/anyone-can-code/issues/new?template=bug_report.yml) |
| Tracked feature | [GitHub Issues — Feature](https://github.com/mitunmanav/anyone-can-code/issues/new?template=feature_request.yml) |
| Security | [SECURITY.md](SECURITY.md) — **not** public issues or Discussions |
| Docs map | [docs/README.md](../docs/README.md) |

**Rule of thumb:** question or idea → **Discussions**. Something broken → **Issues**.

## Discussions (easiest first)

1. Read [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5).  
2. Open the matching category form (Q&A, Ideas, …).  
3. Answer the short prompts — plain language is enough.

Guide: [DISCUSSIONS.md](DISCUSSIONS.md) · Browse: [all discussions](https://github.com/mitunmanav/anyone-can-code/discussions)

## Before opening a **bug** issue

1. Read the [README](../README.md) install steps.  
2. Run (remove secrets before sharing):

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
```

3. Include: OS, plugin version (Releases or `plugin.json`), what you ran, expected vs actual.

Every **issue** gets an automatic **AI maintainer brief** (plain English). Re-run: comment `/ai-review`.

**Do not paste:** tokens, private paths, full memory notes, personal data.
