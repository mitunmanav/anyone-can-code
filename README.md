<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Plain English → plan → build → check.</strong><br/>
  Free Codex plugin for people who are not engineers.<br/>
  Say what you want. ACC helps you plan, build, and check that it works.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Beta"/>
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Install free</strong></a>
  ·
  <a href="docs/FIRST_DAY.md">First day</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Report a problem</a>
</p>

<p align="center">
  <strong>Languages:</strong>
  English ·
  <a href="readmes/README.pt-BR.md">Português</a> ·
  <a href="readmes/README.es.md">Español</a> ·
  <a href="readmes/README.zh-CN.md">简体中文</a> ·
  <a href="readmes/README.ja.md">日本語</a> ·
  <a href="readmes/README.ko.md">한국어</a> ·
  <a href="readmes/README.hi.md">हिन्दी</a> ·
  <a href="readmes/README.fr.md">Français</a> ·
  <a href="readmes/README.de.md">Deutsch</a>
</p>

---

## What it is

**Anyone Can Code (ACC)** is a free open-source plugin for [OpenAI Codex](https://openai.com/codex/).  
Not a new agent. Not an IDE. **Codex writes the code.** ACC gives the work a clear path.

| Step | What you get |
|------|----------------|
| **Plan** | A clear path before big changes |
| **Build** | Work done step by step in your project |
| **Check** | A real “is it done?” pass — not just “looks fine” |
| **Remember** | **Desktop + CLI:** auto memory when hooks trusted (`$learn` / `$wiki` optional) |

**One plugin** for Desktop and CLI — same name: **Anyone Can Code**.

Open beta · **v2.0.0-beta.5** · one plugin Desktop + CLI · auto memory when hooks trusted.

**Need:** [Codex](https://openai.com/codex/) (Desktop and/or CLI) · Python 3

I’m **Mitun**. One product I shipped with ACC: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

---

## Install — Desktop

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code in Codex Desktop" width="560"/>
</p>

1. Copy: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → paste
3. Install **Anyone Can Code**
4. **Hooks** → enable + **trust every ACC hook** (required)
5. Restart → open a project folder → `$setup` → say what you want

Video: [website](https://anyone-can-code.vercel.app/#install) · [mp4](docs/media/install-setup.mp4)

---

## Install — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. In a project folder: `codex`
2. `/plugins` → install **Anyone Can Code** (same plugin as Desktop)
3. `/hooks` → **trust** every ACC hook
4. New thread → `$setup` → say what you want

---

## Desktop & CLI

**One plugin.** Same ACC work on both. Only host chrome differs.

| | Desktop | CLI |
|--|---------|-----|
| **Auto memory** (hooks trusted) | Yes | Yes |
| **Skills** (`$setup`, `$verify`, …) | Yes | Yes |
| **Plan → build → check** | Yes | Yes |
| **Fail-closed safety** | Yes | Yes |
| **Trust hooks** | Hooks UI | `/hooks` |
| **Install** | Plugins UI | marketplace cmd + `/plugins` |
| **Review** | Review pane or `/review` | `/review` |
| **Scheduled ACC jobs** | Desktop/web only | — |
| **Sites / app browser** | Desktop only | — |

Memory lives on your machine under `.codex/anyone-can-code/`. Not sent to ACC servers.

**Tip:** After plugin update, re-trust hooks, then restart.

More detail: [website](https://anyone-can-code.vercel.app/).

---

## Everyday use

You can also just talk in plain English.

| Type | When |
|------|------|
| `$setup` | First time in a project |
| `$status` / `$help` | Where am I? What’s next? |
| `$resume` | Continue after a break |
| `$verify` | Is this actually done? |
| `$fix` | Same error keeps happening |

Example: *“Build a simple expense tracker and explain each step in plain English.”*

Full first session: **[docs/FIRST_DAY.md](docs/FIRST_DAY.md)**

---

## If something fails

| Problem | Fix |
|---------|-----|
| Marketplace won’t add | Use the **full** GitHub URL above |
| Nothing works after install | **Trust all ACC hooks**, restart, new chat |
| Forgets on Desktop | Hooks not trusted (or not re-trusted after update) |
| Forgets on CLI | Hooks not trusted (or not re-trusted after update) — same fix as Desktop |
| Old “CLI only” package | Uninstall **Anyone Can Code CLI**; install **Anyone Can Code** once |
| `$setup` silent | Open a **project folder** first |

Still stuck? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Links

[Website](https://anyone-can-code.vercel.app/) · [Roadmap](ROADMAP.md) · [First day](docs/FIRST_DAY.md) · [Privacy](docs/PRIVACY.md) · [Terms](docs/TERMS.md) · [Contributing](.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
