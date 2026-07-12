<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Languages:</strong>
  English ·
  <a href="i18n/README.pt-BR.md">Português</a> ·
  <a href="i18n/README.es.md">Español</a> ·
  <a href="i18n/README.zh-CN.md">简体中文</a> ·
  <a href="i18n/README.ja.md">日本語</a> ·
  <a href="i18n/README.ko.md">한국어</a> ·
  <a href="i18n/README.hi.md">हिन्दी</a> ·
  <a href="i18n/README.fr.md">Français</a> ·
  <a href="i18n/README.de.md">Deutsch</a>
</p>

<p align="center">
  <strong>A Codex Desktop plugin for people who are not engineers.</strong><br/>
  Say what you want in plain English. ACC helps you plan, build, and check that it actually works.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/Windows%20·%20Codex-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Beta"/>
</p>

---

## What it is

**Anyone Can Code (ACC)** is a free plugin for **Codex Desktop** on Windows. It is built for non-technical people — including me.

You describe an idea, a fix, or a project in normal words. ACC walks you through:

| Step | What you get |
|------|----------------|
| **Plan** | A clear path before big changes |
| **Build** | Work done step by step in your project |
| **Check** | A real “is it done?” pass, not just “looks fine” |

It is a **native Codex** plugin — written from [Codex official docs](https://openai.com/codex/), not ported from Claude, Cursor, or other agents.

I’m **Mitun**. I use ACC myself. One real product I shipped with it: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2). Open beta: **v1.1.0-beta.3**.

**You need:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Install

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code in Codex Desktop" width="640"/>
</p>

1. Copy this URL: `https://github.com/mitunmanav/anyone-can-code`
2. In Codex → **Plugins** → **+** → **Add a Marketplace** → paste the URL
3. Find **Anyone Can Code** → **Install**
4. Open **Hooks** → turn on every ACC hook and **trust** each one (required — Codex does not auto-trust)
5. **Restart** Codex and confirm the plugin tools are on
6. Open a project folder → run `$setup` → say what you want to build

Optional (marketplace only — you still need hooks, restart, then `$setup`):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Video file: [docs/media/install-setup.mp4](docs/media/install-setup.mp4) · Full walkthrough on the site: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## If something fails

| What you see | What to try |
|--------------|-------------|
| Marketplace / install fails | Paste the **full** GitHub URL above, not a short name |
| Plugin installed but nothing works | Trust **all** ACC hooks, then fully restart Codex |
| `$setup` does nothing | Open a **project folder** first, start a **new chat**, try `$setup` again |
| Still stuck | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) or [report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

[Discord](https://discord.gg/qgS29y7TqP) is fine for quick questions. Use Issues when something is broken.

---

## Useful commands

You can also just talk in plain English. These help when you want a clear switch:

| Command | When to use it |
|---------|----------------|
| `$setup` | First time in a project — get ready to work |
| `$orchestrator` | Main front door when you are not sure where to start |
| `$help` / `$status` | Where you are and what is next |
| `$resume` | Continue after a break |
| `$verify` | Check that work is really done |
| `$fix` | When the same thing keeps failing |

---

## Links

[Website](https://anyone-can-code.vercel.app/) · [Roadmap](ROADMAP.md) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [Privacy](docs/PRIVACY.md) · [Terms](docs/TERMS.md) · [Contributing](.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
