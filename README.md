<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="240"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>A reliability workflow plugin for OpenAI Codex.</strong><br/>
  Codex does the coding. ACC helps you plan, build, and check the work.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Open beta"/>
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

---

## What it is

Free open-source **plugin** for [OpenAI Codex](https://openai.com/codex/) — Desktop and CLI.

Not a new agent. Not an IDE. Codex writes the code. ACC gives the work a clear path:

| | |
|--|--|
| **Plan** | Make the request clear. Break big work into steps. |
| **Build** | Work step by step. Keep progress on your machine. |
| **Check** | Prove what works before calling it “done.” |

You talk in plain English. Open beta **v1.1.0-beta.4**.

Need: Codex (Desktop and/or CLI) · Python 3

---

## Pick one package

Same marketplace. **Two plugins.** Install the one that matches how you use Codex.

| You use | Install this |
|---------|----------------|
| Codex **Desktop** app | **Anyone Can Code** |
| Codex **CLI** terminal | **Anyone Can Code CLI** |

Do **not** install both unless you use both.  
More detail: [Desktop package](plugins/anyone-can-code/README.md) · [CLI package](plugins/anyone-can-code-cli/README.md)

---

## Install

### Desktop

1. Copy: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → paste  
3. Install **Anyone Can Code** (not the CLI name)  
4. **Hooks** → enable + **trust every ACC hook** (required)  
5. Restart → open a project folder → `$setup` → say what you want  

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code in Codex Desktop" width="560"/>
</p>

Video: [website](https://anyone-can-code.vercel.app/#install) · [mp4 in repo](docs/media/install-setup.mp4)

### CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. In a project folder: `codex`  
2. `/plugins` → install **Anyone Can Code CLI**  
3. `/hooks` → **trust** every ACC hook  
4. New thread → `$setup` → say what you want  

---

## Everyday use

| Type | When |
|------|------|
| `$setup` | First time in a project |
| `$status` / `$help` | Where am I? What’s next? |
| `$resume` | Continue after a break |
| `$verify` | Is this actually done? |
| `$fix` | Same error keeps happening |

You can also just talk in normal words.

Example: *“Build a simple expense tracker and explain each step in plain English.”*

Full first session: **[docs/FIRST_DAY.md](docs/FIRST_DAY.md)**

---

## If something fails

| Problem | Fix |
|---------|-----|
| Marketplace won’t add | Use the **full** GitHub URL above |
| Nothing works after install | **Trust all ACC hooks**, then restart / new chat |
| `$setup` silent | Open a **project folder** first |
| Wrong package | Uninstall; install Desktop **or** CLI for your host |

Still stuck? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## More

| | |
|--|--|
| Website | https://anyone-can-code.vercel.app/ |
| Roadmap | [ROADMAP.md](ROADMAP.md) |
| Privacy | [docs/PRIVACY.md](docs/PRIVACY.md) |
| Contributing | [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) |
| Languages | [Português](readmes/README.pt-BR.md) · [Español](readmes/README.es.md) · [中文](readmes/README.zh-CN.md) · [日本語](readmes/README.ja.md) · [한국어](readmes/README.ko.md) · [हिन्दी](readmes/README.hi.md) · [Français](readmes/README.fr.md) · [Deutsch](readmes/README.de.md) |

MIT · Built by [Mitun](https://github.com/mitunmanav)
