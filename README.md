<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>A Codex Desktop plugin for non-technical people.</strong><br/>
  Say what you want in plain English. ACC helps plan, build, and check the work.
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
  <a href="#how-to-install">How to install</a>
  ·
  <a href="https://anyone-can-code.vercel.app/#install">Video guide</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/discussions/5">Start here</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Report a problem</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
</p>

---

## What is this?

**Anyone Can Code (ACC)** is a free **plugin** for **[Codex Desktop](https://openai.com/codex/)** on **Windows**.

It is for people who are **not** technical — including the person who built it.

| You do this | ACC helps with |
|-------------|----------------|
| Say what you want in normal words | A clear plan |
| Work on your idea or project | Building step by step |
| Ask “is this done?” | Checking work before “done” |

**Not** a coding class. **Not** an engineering product.  
A practical plugin when other plugins and workflows feel too hard.

**Open beta** (v1.1.0-beta.3) · MIT · still improving

### Why it exists

Mitun is non-technical. For **more than a year** he tried many AI tools. Most were confusing, scattered, or made for engineers.

He still does not claim a perfect “final system.” He found a path that **works for him** — and he is building ACC so people like him can use AI without engineering knowledge.

**Real example:** while testing ACC, he used it to help ship **[Everything AI](https://github.com/mitunmanav/everything-ai)** toward **[v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)**.

---

## Before you install

1. **Windows** computer  
2. **[Codex Desktop](https://openai.com/codex/)** installed and opening normally  
3. **Python** available (Codex often needs this for plugins)

Install Codex first if you do not have it yet.

---

## How to install

> **Watch first (recommended):** [Install video on the website](https://anyone-can-code.vercel.app/#install)  
> Same steps are written below.

### Step 1 — Copy this repo’s URL

On this GitHub page, click the green **Code** button and copy the HTTPS URL:

```text
https://github.com/mitunmanav/anyone-can-code
```

(Or copy that line as-is.)

### Step 2 — Add the marketplace in Codex

1. Open the **Codex** app  
2. Click **Plugins**  
3. Click the **+** (plus) in the **top-right**  
4. Open the small **dropdown** next to it  
5. Choose **Add a Marketplace**  
6. Paste the GitHub URL into the field at the top  
7. Confirm / add  

Codex now knows where ACC lives.

### Step 3 — Install the plugin

1. Stay in **Plugins**  
2. **Scroll down** to the marketplace list  
3. Find **Anyone Can Code**  
4. Click **Install**

### Step 4 — Trust hooks (required)

**This step is mandatory.** Hooks cannot be auto-trusted for you. There is **no** automatic bypass.

1. In Plugins / ACC, open **Hooks**  
2. Open **Settings**  
3. **Enable** every ACC hook  
4. **Trust** every ACC hook  

If hooks are off or untrusted, the plugin **will not work properly**.

### Step 5 — Restart and check tools

1. **Fully quit** Codex and open it again  
2. Confirm ACC is installed  
3. Confirm **hooks** are still enabled and trusted  
4. Confirm related **tools** for the plugin are enabled  

### Step 6 — Start using it

1. Open a **project folder** in Codex  
2. Start a **new chat**  
3. Type:

```
$setup
```

4. Then say what you want in plain English, for example:

```
I want a simple website with a contact form
```

Or type `$orchestrator` and follow the prompts.

---

### Optional: terminal marketplace command

If you prefer the command line instead of the Plugins UI:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Then still do **Steps 3–6** in Codex (install plugin, **trust hooks**, restart, `$setup`).

---

## If something goes wrong

| Problem | What to try |
|---------|-------------|
| Marketplace will not add | Paste the full GitHub URL: `https://github.com/mitunmanav/anyone-can-code` |
| Plugin not listed | Add marketplace again, scroll the list, restart Codex |
| Plugin installed but “does nothing” | Open Hooks → Settings → **enable + trust all** → restart |
| `$setup` no reply | New chat **inside** a project folder; check hooks again |
| Tools missing | After restart, open plugin settings and enable tools |

Still stuck?

- [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)  
- [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5)  
- [Discord](https://discord.gg/qgS29y7TqP)  
- [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) (plain English is fine)

---

## Commands you’ll use most

Type these in the Codex chat:

| Type this | What it does |
|-----------|----------------|
| `$setup` | First-time setup for this project |
| `$orchestrator` | Front door — helps pick the next step |
| `$help` | Where you are, in plain language |
| `$status` | Current task and what’s next |
| `$resume` | Continue after a break |
| `$verify` | Check work with proof |
| `$fix` | Help when the same thing keeps failing |

You can also just **talk normally**. Commands are shortcuts.

More detail: [plugin README](plugins/anyone-can-code/README.md)

---

## What ACC tries to do well

- Plan first, then build  
- Ask only the questions that unblock you  
- Remember important decisions on **your** computer  
- Avoid saying “done” without checking  
- Stay usable for non-technical people  

Privacy: [docs/PRIVACY.md](docs/PRIVACY.md)

---

## Get help

| I want to… | Open this |
|------------|-----------|
| Watch install | [Website install section](https://anyone-can-code.vercel.app/#install) |
| Read install again | [How to install](#how-to-install) |
| Ask a question | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) |
| Chat live | [Discord](https://discord.gg/qgS29y7TqP) |
| Report something broken | [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

**Simple rule:** questions → Discussions/Discord · broken → Report a problem.

---

## For people who change the code

Most users can skip this.

| Path | What |
|------|------|
| `plugins/anyone-can-code/` | Plugin |
| `.github/` | Issues, CI, community docs |
| `docs/` | Privacy, terms — [map](docs/README.md) |
| `CHANGELOG.md` | Release notes |

```bash
python -m pytest plugins/anyone-can-code/tests -q
```

[CONTRIBUTING.md](.github/CONTRIBUTING.md) · [SAFETY.md](.github/SAFETY.md) · [PRIVACY](docs/PRIVACY.md) · [TERMS](docs/TERMS.md)

---

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)

<p align="center">
  <sub>MIT License · <a href="https://github.com/mitunmanav">Mitun</a> · <a href="https://anyone-can-code.vercel.app/">Website</a></sub>
</p>
