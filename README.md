<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Plain English → plan → build → check.</strong><br/>
  Free Codex plugins (Desktop + CLI) for people who are not engineers.<br/>
  Say what you want. ACC helps you plan, build, and check that it actually works.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="ROADMAP.md"><img src="https://img.shields.io/badge/roadmap-public-0A66C2?style=flat-square" alt="Roadmap"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/Desktop-0078D4?style=flat-square" alt="Desktop"/>
  <img src="https://img.shields.io/badge/CLI-111827?style=flat-square" alt="CLI"/>
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

Free open-source **plugins** for [OpenAI Codex](https://openai.com/codex/).  
Not a new agent. Not an IDE. **Codex writes the code.** ACC gives the work a clear path:

| Step | What you get |
|------|----------------|
| **Plan** | A clear path before big changes |
| **Build** | Work done step by step in your project |
| **Check** | A real “is it done?” pass — not just “looks fine” |
| **Remember** | **Desktop:** full auto memory. **CLI:** not yet (use `$learn` / `$wiki` for now) |

Native Codex — built from [Codex docs](https://openai.com/codex/), not ported from Claude or Cursor.

I’m **Mitun**. One product I shipped with ACC: [Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2).  
Open beta **v1.1.0-beta.4**.

**Need:** [Codex](https://openai.com/codex/) (Desktop and/or CLI) · Python 3

---

## Pick one package

Same GitHub repo. Same marketplace. **Two plugins.**  
Install the one that matches how you use Codex. Do **not** install both unless you use both.

| You use | Install this |
|---------|----------------|
| Codex **Desktop** app | **Anyone Can Code** |
| Codex **CLI** terminal | **Anyone Can Code CLI** |

More detail: [Desktop](plugins/anyone-can-code/README.md) · [CLI](plugins/anyone-can-code-cli/README.md)

---

## Install — Desktop

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code in Codex Desktop" width="560"/>
</p>

1. Copy: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → paste  
3. Install **Anyone Can Code** (not the CLI name)  
4. **Hooks** → enable + **trust every ACC hook** (required — this is how **Desktop auto memory** works)  
5. Restart → open a project folder → `$setup` → say what you want  

Video: [website](https://anyone-can-code.vercel.app/#install) · [mp4](docs/media/install-setup.mp4)

---

## Install — CLI

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

1. In a project folder: `codex`  
2. `/plugins` → install **Anyone Can Code CLI**  
3. `/hooks` → **trust** every ACC hook (required for guards + session load/save)  
4. New thread → `$setup` → say what you want  

**Note:** CLI does **not** have full auto memory yet. Desktop first. CLI can still use `$learn` / `$wiki` / `$capture` by hand.

---

## Memory (automatic on Desktop)

| Host | Auto memory in beta.4? |
|------|-------------------------|
| **Codex Desktop** + **Anyone Can Code** | **Yes** — full offline auto memory |
| **Codex CLI** + **Anyone Can Code CLI** | **Not yet** — focus is Desktop first; save by hand with `$learn` / `$wiki` / `$capture` |

### Desktop — what sticks (no save command)

You do **not** type a “save this” command in normal Desktop use. After hooks are trusted, ACC writes and reloads memory for you.

| Kind | Example |
|------|---------|
| **Wants / prefs** | “Always use the blue theme.” |
| **Decisions** | “We’ll use SQLite for storage.” |
| **Corrections** | “No — contact page, not about.” |
| **Open work** | Goal, next step, unfinished ask after a crash |

### How Desktop auto memory works (plain English)

1. **You talk** — ACC’s hooks quietly record what matters.  
2. **You leave, crash, or hit a limit** — the last open request is marked so the next session can show a **crash-resume** line.  
3. **You open a new chat** — SessionStart loads **NOW** (goal + next) plus top lessons.  
4. **Stays on your machine** under `.codex/anyone-can-code/memory/` (notes + live `NOW.md`). Nothing is sent to ACC servers.

Trust hooks once, and again after every plugin update (hook hash changes).

### Desktop — what you do *not* need

- No `$learn` / `$capture` as the normal path on Desktop. Those are **backup / force** only if something looks wrong.  
- No Codex built-in `/memories` for ACC’s project memory. ACC keeps its own local notes.

### If Desktop memory seems dead

| Check | Fix |
|-------|-----|
| Forgot between sessions | **Trust all ACC hooks**, restart Codex, new chat |
| After a plugin update | Trust hooks **again**, then restart |
| Want a health check | Run `python3 plugins/anyone-can-code/scripts/memory_doctor.py` in the plugin folder — should say memory is running, or tell you to trust hooks |

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
| Nothing works after install | **Trust all ACC hooks**, then restart / new chat |
| Forgets what you decided (Desktop) | Hooks not trusted (or not re-trusted after update) — see [Memory](#memory-automatic-on-desktop) |
| Expects auto memory on CLI | Not shipped yet — use `$learn` / `$wiki`, or use Desktop |
| Wrong package | Uninstall; install Desktop **or** CLI for your host |
| `$setup` silent | Open a **project folder** first |

Still stuck? [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discord](https://discord.gg/qgS29y7TqP) · [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)

---

## Roadmap

| When | Focus |
|------|--------|
| **Now · beta.4** | **Desktop** auto memory (trust hooks) · plain progress · honest push-back · safety |
| **Next · beta.5** | Plays-nice plugins · smarter model choice · less lost work at limits · CLI memory later |

Full detail: **[ROADMAP.md](ROADMAP.md)** · [website](https://anyone-can-code.vercel.app/#roadmap)

---

## Links

[Website](https://anyone-can-code.vercel.app/) · [Roadmap](ROADMAP.md) · [First day](docs/FIRST_DAY.md) · [Privacy](docs/PRIVACY.md) · [Terms](docs/TERMS.md) · [Contributing](.github/CONTRIBUTING.md)

MIT · Built by [Mitun](https://github.com/mitunmanav)
