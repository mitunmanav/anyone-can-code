# Privacy Policy — Anyone Can Code

_Last updated: 2026-07-11_

## Short version

Anyone Can Code is a local Codex plugin (one package for Desktop and CLI). It does not collect, transmit, or sell your data. There is no account and no waitlist signup through the plugin.

## Product website

The marketing/install site at [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) is separate from the plugin. That site is a static product page (install and overview). It does not require a waitlist or account to use the open-source plugin.

## What the plugin stores

All plugin data lives on your machine, under your project folder:

```text
.codex/anyone-can-code/
```

Typical contents:

- Workflow state (what you are building, what is next)
- Portable Markdown memory notes (auto memory when hooks are trusted; `$learn` / `$wiki` as backup)
- Local logs used for verification and debugging

Nothing from that folder is sent to Anyone Can Code servers. This project does not operate a plugin telemetry or analytics backend.

## What the plugin does not do

- No account, no sign-up, no plugin-side tracking
- No network calls of its own — network activity (if any) goes through Codex under your control
- No reading of files outside the project you opened (except normal Codex/tool behavior you approve)

## Your data, your control

Delete `.codex/anyone-can-code/` in a project to remove that project’s plugin state.

## Questions

- Issues: [github.com/mitunmanav/anyone-can-code/issues](https://github.com/mitunmanav/anyone-can-code/issues)
- Security (private): [SECURITY.md](../.github/SECURITY.md)
