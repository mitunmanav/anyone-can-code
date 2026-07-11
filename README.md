<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Codex Desktop plugin for non-technical people.</strong><br/>
  Say what you want in plain English. Plan → build → check.
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

Free **Codex Desktop** plugin (Windows). Built for people who are **not** engineers — including me.

| You | ACC |
|-----|-----|
| Say what you want | Helps plan |
| Work on an idea or folder | Helps build |
| Ask if it’s done | Helps verify |

Native Codex — built from **Codex official docs**, not migrated from Claude/Cursor/other agents.  
Open beta (v1.1.0-beta.3). I’m Mitun; I used ACC while shipping [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).

**Need:** Windows · [Codex Desktop](https://openai.com/codex/) · Python

---

## Install

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code" width="640"/>
</p>

1. Copy: `https://github.com/mitunmanav/anyone-can-code`  
2. Codex → **Plugins** → **+** → **Add a Marketplace** → paste URL  
3. Find **Anyone Can Code** → **Install**  
4. **Hooks** → enable + **trust every ACC hook** (required — no auto-trust)  
5. **Restart** Codex · confirm tools on  
6. Open a project → `$setup` → say what you want  

Optional terminal (marketplace only — still do hooks + restart):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

MP4: [docs/media/install-setup.mp4](docs/media/install-setup.mp4) · Site: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/#install)

---

## Stuck?

| Problem | Fix |
|---------|-----|
| Marketplace fails | Full GitHub URL |
| Nothing happens | Trust **all** hooks → restart |
| `$setup` silent | New chat in a project folder |

[FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) · [Discord](https://discord.gg/qgS29y7TqP)

---

## Commands

| Type | Does |
|------|------|
| `$setup` | First setup |
| `$orchestrator` | Front door |
| `$help` / `$status` | Where am I / what’s next |
| `$resume` | Continue |
| `$verify` | Check with proof |
| `$fix` | When it keeps failing |

Or just talk in plain English.

---

## Links

Website · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) · [Privacy](docs/PRIVACY.md) · [Terms](docs/TERMS.md) · [Contributing](.github/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
