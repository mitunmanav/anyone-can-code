<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code logo" width="280"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>A reliability workflow plugin for OpenAI Codex.</strong><br/>
  Say what you want. ACC helps Codex <strong>plan it, build it, and prove it works</strong>.
</p>

<p align="center">
  Codex does the coding. ACC gives the work a reliable path from idea to verified result—so you can build without blindly trusting “done.”
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

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="ROADMAP.md"><img src="https://img.shields.io/badge/roadmap-public-0A66C2?style=flat-square" alt="Roadmap"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/Desktop-0078D4?style=flat-square" alt="Codex Desktop package"/>
  <img src="https://img.shields.io/badge/CLI-111827?style=flat-square" alt="Codex CLI package"/>
  <img src="https://img.shields.io/badge/beta-orange?style=flat-square" alt="Open beta"/>
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/#install"><strong>Install free</strong></a>
  ·
  <a href="docs/FIRST_DAY.md">First day</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/releases">Releases</a>
  ·
  <a href="https://discord.gg/qgS29y7TqP">Discord</a>
  ·
  <a href="https://github.com/mitunmanav/anyone-can-code/issues/new/choose">Report a problem</a>
</p>

---

## The problem

Codex can write a lot of code fast. That is not the hard part.

The hard part is:

- Starting from a vague idea and ending with a **clear path**
- Keeping work **alive across sessions** when you stop, hit limits, or restart
- Knowing what is **actually done** vs what only *looks* done
- Recovering after errors, thrash, and half-finished attempts
- Trusting “done” when you **cannot** confidently read every line

Without structure, sessions drift: chaotic changes, forgotten context, repeated mistakes, and confident claims with thin proof.

---

## What ACC changes

Anyone Can Code (ACC) is a **free, open-source plugin for OpenAI Codex** — not a new coding agent, not an IDE, not a replacement for Codex.

It is a **reliability and execution layer** on top of Codex:

| Outcome | What that means in practice |
|---------|------------------------------|
| **Plain English** | Describe the result you want without learning a long command language first |
| **Structure** | Clarify → plan → execute in steps, with tracked tasks and boundaries |
| **Continuity** | Local project state and notes so work can resume later |
| **Honest progress** | Separate implemented, verified, blocked, deferred, and uncertain |
| **Verification** | “Done” needs evidence (tests, checks, observed behaviour) — or a clear gap |
| **Recovery** | Resume, reconstruct, or repair after interrupts and failures |
| **Local control** | Workflow state lives under `.codex/anyone-can-code/` on your machine |
| **Native Codex** | Official plugin shape (skills + hooks + marketplace) for Desktop and CLI |

**Primary statement:** ACC turns plain-English requests into **planned, resumable, verified** Codex work.

---

## How Plan → Build → Check works

| Stage | Skill path | What happens |
|-------|------------|--------------|
| **Plan** | `$clarify` · `$plan` · `$orchestrator` | Make the request concrete. Build an ordered path with dependencies and check targets — not one uncontrolled generation. |
| **Build** | `$execute` · `$status` · `$capture` · `$learn` | Work step by step. Keep useful project context and progress on disk. |
| **Check** | `$verify` · `$fix` · review | Record what passed, failed, or stays uncertain. Built ≠ verified. |

**Codex does the coding.** ACC shapes how the work is planned, remembered, recovered, and claimed complete.

You can type skill names or just talk in normal English after `$setup`.

---

## Who it is for

| Audience | Why ACC helps |
|----------|----------------|
| **Primary — non-technical builders** | Founders, students, operators, creators who use Codex but should not have to trust “looks fine” |
| **Secondary — developers** | People who want repeatable plan/memory/verify/recover behaviour in Codex |
| **Tertiary — plugin builders** | People studying Codex-native reliability workflows (hooks, skills, local state) |

ACC is **not** “for everyone” in the abstract. It is for people who want a **reliable path through Codex work**, especially when they cannot audit every line themselves.

---

## What makes it different

Codex plugins today include integrations, skill packs, role packs, and planning or review helpers. ACC’s category is narrower:

**A Codex reliability workflow** — one continuous path:

**Plain English → clarify → plan → build → remember → recover → verify → report honestly.**

| Category | Typical focus | ACC |
|----------|---------------|-----|
| General AI coding assistant | Write code in chat | Uses Codex; does not replace it |
| Prompt / skill collections | Reusable instructions | Full workflow + local state + hooks |
| Planning-only tools | Specs and task lists | Plan **and** execute, resume, verify |
| Review / test-only plugins | Diffs and QA after the fact | Verification is built into the loop |
| Multi-agent orchestration platforms | Many agents / hosts | Stays **inside** Codex (Desktop or CLI) |
| No-code app builders | Drag-and-drop products | Software work through Codex, not a new builder |

No competitor attacks. Own the category: **Codex reliability workflow.**

Native implementation from [official Codex patterns](https://openai.com/codex/) — not a loose port of Claude Code / Cursor rule packs.

---

## Desktop vs CLI (pick one)

Same GitHub marketplace. **Two separate packages.** Codex does **not** auto-pick.

| | **Anyone Can Code** | **Anyone Can Code CLI** |
|--|---------------------|-------------------------|
| **Host** | Codex **Desktop** app | Codex **CLI** (`codex` in terminal) |
| **Marketplace name** | Anyone Can Code | Anyone Can Code CLI |
| **Repo folder** | `plugins/anyone-can-code/` | `plugins/anyone-can-code-cli/` |
| **Install UI** | App → **Plugins** | CLI → **`/plugins`** |
| **Trust hooks** | App Hooks settings | CLI → **`/hooks`** |
| **Package README** | [Desktop package](plugins/anyone-can-code/README.md) | [CLI package](plugins/anyone-can-code-cli/README.md) |

**Do not install both** unless you use both hosts. Wrong package + untrusted hooks = “installed but nothing works.”

---

## Fast installation

### Desktop

<p align="center">
  <img src="docs/media/install-setup.gif" alt="Install Anyone Can Code in Codex Desktop: add marketplace, install plugin, trust hooks" width="640"/>
</p>

1. Copy: `https://github.com/mitunmanav/anyone-can-code`
2. Codex Desktop → **Plugins** → **+** → **Add a Marketplace** → paste the URL  
3. Install **Anyone Can Code** (Desktop) — not **Anyone Can Code CLI** unless you also use the terminal  
4. **Hooks** → enable + **trust** every ACC hook (required; Codex does not auto-trust)  
5. Restart Codex · open a **project folder** · new chat → `$setup` → say what you want  

Video: [docs/media/install-setup.mp4](docs/media/install-setup.mp4) · [Website walkthrough](https://anyone-can-code.vercel.app/#install)

### CLI

1. Add marketplace (once):

```bash
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

2. In a project folder: `codex`  
3. **`/plugins`** → install **Anyone Can Code CLI**  
4. **`/hooks`** → review + **trust** ACC hooks  
5. New thread → `$setup` → say what you want  

**You need:** [OpenAI Codex](https://openai.com/codex/) (Desktop and/or CLI) · **Python 3** on the machine (plugin scripts)

**Open beta:** [v1.1.0-beta.4](https://github.com/mitunmanav/anyone-can-code/releases/tag/v1.1.0-beta.4) · [First day guide](docs/FIRST_DAY.md)

---

## First five minutes

1. Install the package that matches your host and **trust hooks**.  
2. Open the project folder; start a **new** chat/thread.  
3. Run `$setup` and answer the short questions.  
4. Try a small ask:

```text
Plan a tiny first version. Do not write lots of code yet.
```

5. Check orientation: `$status` or `$help`. Before you trust “done”: `$verify`.

---

## What you can say (examples)

These show the **workflow**, not only command names:

| You say | What ACC optimises for |
|---------|-------------------------|
| “Build a simple expense tracker and explain each decision in plain English.” | Clarify scope → plan → build in steps → check |
| “Continue the unfinished authentication work and tell me what is actually complete.” | Resume from local state · honest progress |
| “Fix this recurring error, test the fix, and show me the evidence.” | `$fix` / repair path · verification record |
| “Review this project and separate verified problems from guesses.” | Evidence levels · uncertainty named |
| “Prepare this project for release and clearly list anything still unsafe or unverified.” | Ship gate mindset · gaps explicit |

Useful short commands (both packages):

| Command | When |
|---------|------|
| `$setup` | First time in a project |
| `$orchestrator` | Not sure where to start |
| `$help` / `$status` | Orientation |
| `$plan` / `$execute` | Structured plan and build |
| `$resume` | Continue after a break or interrupt |
| `$verify` | Evidence before “done” |
| `$fix` | Same failure keeps repeating |
| `$handoff` | Leave a clean next-session packet |

CLI-only tips: long job → `/goal` · before ship → `/review` · model → `/model`

Full skill list: [Desktop package README](plugins/anyone-can-code/README.md) · [CLI package README](plugins/anyone-can-code-cli/README.md)

---

## Verification and honest completion

`$verify` writes an evidence-oriented record (typically under `.codex/anyone-can-code/artifacts/`). Workflow language separates:

- **implemented** — built, not yet proven  
- **verified** — evidence exists for the claim  
- **blocked** / **deferred** / **uncertain** — named gaps  

ACC does **not** guarantee bug-free software. It makes completion **checkable**: what ran, what passed, what did not, what remains unknown.

---

## Local state, privacy, and safety

| Topic | Fact |
|-------|------|
| **Where state lives** | Project-local `.codex/anyone-can-code/` (workflow, notes, artifacts, logs) |
| **Telemetry** | Plugin does not run a product analytics backend; no ACC account |
| **Network** | Work goes through Codex under your control; see [PRIVACY.md](docs/PRIVACY.md) |
| **Hooks** | Must be **trusted** or the plugin is effectively inert |
| **Safety** | Security/deploy-style gates fail closed when checks cannot run; see [.github/SAFETY.md](.github/SAFETY.md) |
| **Secrets** | Never commit keys or paste them into issues; private vulns → [SECURITY.md](.github/SECURITY.md) |

Delete `.codex/anyone-can-code/` in a project to remove that project’s ACC data.

---

## Current beta status and limitations

| Status | Detail |
|--------|--------|
| **Version** | **1.1.0-beta.4** open beta ([releases](https://github.com/mitunmanav/anyone-can-code/releases)) |
| **Hosts** | Codex Desktop **or** Codex CLI (separate packages) |
| **OS** | Windows-first heritage; Desktop/CLI also used on macOS/Linux where Codex runs — still beta |
| **Runtime** | Python 3 for plugin scripts |
| **Not claimed** | Zero bugs · full autonomy · guaranteed completion · guaranteed security · “never need technical help” |
| **Known friction** | Wrong package, untrusted hooks, or no project folder → silent failure feel |

Plans can change: **[ROADMAP.md](ROADMAP.md)** · [roadmap issue](https://github.com/mitunmanav/anyone-can-code/issues/14)

---

## Demonstrated real-world use

Built with ACC by the author (Mitun): **[Everything AI v0.4.2](https://github.com/mitunmanav/everything-ai/releases/tag/v0.4.2)** — one real product path, not a lab demo count.

---

## Roadmap (short)

| When | Focus |
|------|--------|
| **Now · beta.4** | Desktop + CLI · local two-drawer memory · lessons reload · plain progress · honest push-back · fail-closed safety checks |
| **Next · beta.5** | Plays-nice plugin list · smarter model suggestions · stronger handoff at usage limits |

Full text: [ROADMAP.md](ROADMAP.md) · [Discussion](https://github.com/mitunmanav/anyone-can-code/discussions/13)

---

## If something fails

| Symptom | Try |
|---------|-----|
| Marketplace add fails | Full URL `https://github.com/mitunmanav/anyone-can-code` |
| Wrong package | Uninstall; install Desktop **or** CLI name for your host |
| Installed but idle | Trust **all** ACC hooks · restart / new thread |
| `$setup` silent | Open a **project folder** first · new chat |
| Still stuck | [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [report](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) · [Discord](https://discord.gg/qgS29y7TqP) |

---

## Contributing

Human contributors welcome. See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md).

Local gate (match the package you touch):

```bash
python3 -m pytest plugins/anyone-can-code/tests -q
python3 plugins/anyone-can-code/scripts/doctor.py --json

python3 -m pytest plugins/anyone-can-code-cli/tests -q
python3 plugins/anyone-can-code-cli/scripts/doctor.py --json
```

Repo layout:

```text
plugins/anyone-can-code/       # Desktop package
plugins/anyone-can-code-cli/   # CLI package
.agents/plugins/marketplace.json
```

---

## Support and community

| Link | Use |
|------|-----|
| [Website](https://anyone-can-code.vercel.app/) | Install + product story |
| [First day](docs/FIRST_DAY.md) | First successful session |
| [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) | Common questions |
| [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) | Ideas and show-and-tell |
| [Discord](https://discord.gg/qgS29y7TqP) | Live chat |
| [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose) | Bugs and install failures |
| [Privacy](docs/PRIVACY.md) · [Terms](docs/TERMS.md) | Legal |
| [Support](.github/SUPPORT.md) | Where to get help |

---

## License

[MIT](LICENSE) · Built by [Mitun](https://github.com/mitunmanav) · Site: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/)
