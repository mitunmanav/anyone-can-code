<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>I’m not a programmer. I still wanted to build with AI.</strong><br/>
  So I made a Codex Desktop plugin for people like me.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/platform-Codex%20·%20Windows-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" alt="Beta"/>
</p>

<p align="center">
  <a href="#how-to-install">Install</a>
  ·
  <a href="#watch-the-install">Video</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/discussions/5">Start here</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Report a problem</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
</p>

---

## What this is

**Anyone Can Code (ACC)** is a free **plugin** for **[Codex Desktop](https://openai.com/codex/)** on **Windows**.

You talk like a normal person. ACC helps you plan, build, and check the work before calling it done.

| You | ACC |
|-----|-----|
| Say what you want in plain English | Helps make a plan |
| Work on an idea or a folder | Helps build step by step |
| Wonder if it’s actually finished | Helps check before “done” |

This is **not** a coding course.  
This is **not** built for engineers first.  
It’s for people who tried other plugins and workflows and felt lost.

**Open beta** right now (v1.1.0-beta.3). Things can still break. Tell me when they do.

---

## Why I built it

I’m **Mitun**. I’m non-technical.

For **more than a year** I tried a lot of AI tools. Most of them felt hard, messy, or made for people who already think like programmers. I never found one perfect “final system.” I just found a way I could actually **work** day to day.

I built ACC for that — for me, and for people like me.

While I was testing ACC, I used it to help ship real work, including **[Everything AI](https://github.com/mitunmanav/everything-ai)** toward **[v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)**. That project has its own life. The point is: a non-technical person can use ACC and still ship something.

### Built for Codex from the ground up

ACC is a **native Codex plugin**.

I built it using **Codex official docs** and how Codex plugins, marketplaces, and hooks actually work.

It is **not** a migration from Claude Code, Cursor, Copilot, or any other agent. I didn’t port something else into Codex. I started from Codex.

Other tools and write-ups may have given me *ideas*. The product itself was written for Codex.

---

## Before you install

You need:

1. A **Windows** PC  
2. **[Codex Desktop](https://openai.com/codex/)** installed and opening fine  
3. **Python** available (Codex often needs this for plugins)

If you don’t have Codex yet, install that first.

---

## Watch the install

GitHub shows GIFs well (not MP4). This is the install walkthrough:

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code on Codex Desktop" width="720"/>
</p>

Silent screen recording — same steps written below.

| File | What |
|------|------|
| [`docs/media/install-setup.gif`](docs/media/install-setup.gif) | Preview in this README |
| [`docs/media/install-setup.mp4`](docs/media/install-setup.mp4) | Full video (download if you want) |
| [Website player](https://anyone-can-code.vercel.app/#install) | Video + step labels on the site |

---

## How to install

Same steps as the GIF / video.

### 1. Copy this repo URL

On this page, click green **Code**, or copy:

```text
https://github.com/mitunmanav/anyone-can-code
```

### 2. Add the marketplace in Codex

1. Open **Codex**  
2. Go to **Plugins**  
3. Click the **+** in the top-right  
4. Open the small **dropdown**  
5. Choose **Add a Marketplace** (wording may look like “Add plugin marketplace”)  
6. Paste the GitHub URL  
7. Add it  

If it says the marketplace is already added, that’s fine.

### 3. Install Anyone Can Code

1. Stay in **Plugins**  
2. Scroll and find **Anyone Can Code**  
3. Click **Install**

### 4. Trust the hooks (you must do this yourself)

**This part is required.**  
Hooks cannot be auto-trusted. There is no skip. If you skip this, ACC will not work properly.

1. Open **Hooks** (from the plugin page / settings)  
2. Open **Anyone Can Code** hooks  
3. **Turn on** every ACC hook  
4. **Trust** every ACC hook  

### 5. Restart Codex

1. Fully quit Codex and open it again  
2. Check ACC is still installed  
3. Check hooks are still on and trusted  
4. Check tools/skills for the plugin are enabled  

### 6. Start using it

1. Open a project folder  
2. Start a new chat  
3. Type:

```
$setup
```

4. Then say what you want, for example:

```
I want a simple website with a contact form
```

Or type `$orchestrator` and follow along.

That’s the loop. You can keep talking in normal English after that.

---

### Optional: terminal command

If you like the terminal better for the marketplace part:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

You still need to **install the plugin**, **trust hooks**, **restart**, then run `$setup`. The terminal does **not** skip hooks.

---

## If something goes wrong

| Problem | Try this |
|---------|----------|
| Marketplace won’t add | Paste the full URL: `https://github.com/mitunmanav/anyone-can-code` |
| Can’t find the plugin | Add marketplace again, scroll the list, restart Codex |
| Installed but nothing happens | Hooks → enable + trust **all** → restart |
| `$setup` does nothing | New chat **inside** a project folder; check hooks again |
| Tools missing | After restart, open plugin settings and turn tools on |

Still stuck? That’s okay.

- [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)  
- [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5)  
- [Discord](https://discord.gg/qgS29y7TqP)  
- [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) — plain English is fine  

---

## Commands I use most

Type these in the Codex chat:

| Type this | What it does |
|-----------|----------------|
| `$setup` | First-time setup for this project |
| `$orchestrator` | Front door — helps pick the next step |
| `$help` | Where am I? (plain language) |
| `$status` | Current task and what’s next |
| `$resume` | Continue after a break |
| `$verify` | Check work with proof |
| `$fix` | When the same thing keeps failing |

You can also just talk. Commands are shortcuts when you want them.

More detail: [plugin README](plugins/anyone-can-code/README.md)

---

## What I’m aiming for

- Plan first, then build  
- Only ask questions that actually unblock you  
- Keep notes on **your** computer  
- Don’t say “done” without checking  
- Stay usable for non-technical people  

Privacy: [docs/PRIVACY.md](docs/PRIVACY.md)

---

## Help

| I need… | Go here |
|---------|---------|
| Install video (repo) | [docs/media/install-setup.mp4](docs/media/install-setup.mp4) |
| Install video (website) | [anyone-can-code.vercel.app/#install](https://anyone-can-code.vercel.app/#install) |
| Written install steps | [How to install](#how-to-install) |
| A question | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) |
| Live chat | [Discord](https://discord.gg/qgS29y7TqP) |
| Something broken | [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

**Simple rule:** question → Discussions / Discord · broken → Report a problem.

---

## If you want to change the code

Most people can ignore this.

| Path | What |
|------|------|
| `plugins/anyone-can-code/` | The plugin |
| `docs/media/` | Install video + captions |
| `.github/` | Issues, CI, community docs |
| `docs/` | Privacy, terms — [map](docs/README.md) |
| `CHANGELOG.md` | What changed |

```bash
python -m pytest plugins/anyone-can-code/tests -q
```

[CONTRIBUTING.md](.github/CONTRIBUTING.md) · [SAFETY.md](.github/SAFETY.md) · [PRIVACY](docs/PRIVACY.md) · [TERMS](docs/TERMS.md)

---

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)

<p align="center">
  <sub>MIT · <a href="https://github.com/mitunmanav">Mitun</a> · <a href="https://anyone-can-code.vercel.app/">Website</a></sub>
</p>
