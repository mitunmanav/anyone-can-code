<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>You describe what you want in plain English.</strong><br/>
  It plans, builds, and checks the work — you do not need to be a programmer.
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
  <a href="https://anyone-can-code.vercel.app/">Website</a>
  ·
  <a href="#install-in-3-steps">Install</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/discussions/5">Start here</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Report a problem</a>
</p>

---

## What is this?

**Anyone Can Code (ACC)** is a free add-on for **Codex Desktop** on **Windows**.

1. You say what you want (like talking to a person).  
2. ACC makes a plan.  
3. It helps build the thing.  
4. It **checks the work** before saying “done.”

You do **not** need to know programming.  
This is open source (MIT) and in **open beta** — rough edges can still happen. Tell us if something breaks.

---

## Before you start

You need all three:

1. A **Windows** computer  
2. **[Codex Desktop](https://openai.com/codex/)** installed and working  
3. **Python** installed (Codex often needs this for plugins)

If Codex is not installed yet, do that first, then come back here.

**Current version:** v1.1.0-beta.3

---

## Install in 3 steps

### Step 1 — Add ACC to Codex

1. Open the **Terminal** app on Windows  
   (search “Terminal” or “PowerShell” in the Start menu)  
2. Copy the whole line below  
3. Paste it into the terminal  
4. Press **Enter**

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

This only tells Codex where ACC lives. It does not install the plugin yet.

### Step 2 — Install the plugin

1. Open **Codex Desktop**  
2. Open the **plugin browser** (plugins list)  
3. Find **Anyone Can Code**  
4. Click **Install**  
5. **Restart Codex** (close it fully, open again)

### Step 3 — First project

1. Open a folder for your project (any folder is fine)  
2. Start a new chat in Codex  
3. Type this and press Enter:

```
$setup
```

4. Then say what you want in normal words, for example:

```
I want a simple website with a contact form
```

Or type `$orchestrator` and follow the prompts.

**That’s it.** You can keep chatting in plain English.

---

## If something goes wrong

| What you see | What to try |
|--------------|-------------|
| Command not found / marketplace error | Paste the **full** Step 1 command again, then restart Codex |
| You can’t find Anyone Can Code | Open plugins, search the name, Install, then **restart** Codex |
| `$setup` does nothing | Open a **new chat** inside a project folder and try again |

Still stuck?

- Read the short **[FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)**  
- Or the **[Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5)** guide  
- Or ask on **[Discord](https://discord.gg/qgS29y7TqP)**  
- Or **[report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose)** (guided form — plain English is fine)

---

## Commands you’ll use most

Type these in the Codex chat (with the `$`):

| Type this | What it does |
|-----------|----------------|
| `$setup` | First-time setup for this project |
| `$orchestrator` | “Front door” — helps pick the next step |
| `$help` | Explains where you are, in plain language |
| `$status` | Shows current task and what’s next |
| `$resume` | Continues after you took a break |
| `$verify` | Checks the work with proof |
| `$fix` | Helps when the same thing keeps failing |

You can also just **talk normally**. These commands are shortcuts when you want control.

More detail (optional): [plugin README](plugins/anyone-can-code/README.md)

---

## What ACC is careful about

- It **plans first**, then builds  
- It asks **only the questions that unblock you**  
- It **remembers** important decisions in simple files on your computer  
- It tries **not** to say “done” without checking  
- Your project notes stay **on your machine** (see [Privacy](docs/PRIVACY.md))

---

## Get help (pick one)

| I want to… | Open this |
|------------|-----------|
| See the product page | [Website](https://anyone-can-code.vercel.app/) |
| Install with pictures / short path | [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5) |
| Ask “how do I…?” | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) or [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) |
| Chat with people | [Discord](https://discord.gg/qgS29y7TqP) |
| Report a bug or install failure | [Report a problem](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) |

**Simple rule**

- Question or idea → **Discussions** or Discord  
- Something is broken → **Report a problem** (forms guide you)

You do **not** need perfect technical words. Write like you would text a friend.

---

## For people who want to change the code

Most users can ignore this section.

| Path | What it is |
|------|------------|
| `plugins/anyone-can-code/` | The plugin itself |
| `.github/` | Issues, PR rules, safety, CI |
| `docs/` | Privacy, terms, credits — [full map](docs/README.md) |
| `CHANGELOG.md` | What changed in each release |

```bash
python -m pytest plugins/anyone-can-code/tests -q
```

- How to contribute: [CONTRIBUTING.md](.github/CONTRIBUTING.md)  
- Maintainer safety checklist: [SAFETY.md](.github/SAFETY.md)  
- Privacy · Terms: [PRIVACY](docs/PRIVACY.md) · [TERMS](docs/TERMS.md)

---

<p align="center">
  <sub>MIT · Built by <a href="https://github.com/mitunmanav">Mitun</a> · <a href="https://anyone-can-code.vercel.app/">anyone-can-code.vercel.app</a></sub>
</p>

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date)](https://star-history.com/#mitunmanav/anyone-can-code&Date)
