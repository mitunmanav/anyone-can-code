<p align="center">
  <img src="assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>You describe what you want in plain English.</strong><br/>
  Idea → plan → build → verify. Codex plugin for Desktop + CLI. No programming background required.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/platform-Codex%20Desktop%20%2B%20CLI-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" alt="Beta"/>
</p>

**New here?** Full install (with hooks): [root README — How to install](../../README.md#how-to-install)  

**Install GIF (in this repo):** [docs/media/install-setup.gif](../../docs/media/install-setup.gif)  
**Full video:** [docs/media/install-setup.mp4](../../docs/media/install-setup.mp4) · [website player](https://anyone-can-code.vercel.app/#install)  

**Stuck?** [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5) · [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)

### Install (short)

**Desktop**

1. Copy `https://github.com/mitunmanav/anyone-can-code`  
2. Codex → **Plugins** → **+** → **Add a Marketplace** → paste URL  
3. **Anyone Can Code** → **Install**  
4. Trust every ACC hook (required)  
5. Restart · open a project · `$setup` · say what you want  

**CLI**

1. `codex plugin marketplace add mitunmanav/anyone-can-code --ref main` (or local path)  
2. Run `codex` → `/plugins` → Install **Anyone Can Code**  
3. `/hooks` → trust ACC hooks (required)  
4. New thread · project folder · `$setup` · say what you want  

More: `docs/superpowers/plans/cli-port/cli-install-path.md` (on `grok` branch).

**Current version:** [plugin.json](.codex-plugin/plugin.json) · [Releases](https://github.com/mitunmanav/anyone-can-code/releases)

---

## Everyday commands (start here)

Type these in the Codex chat (or pick the short **ACC …** name in the app). You can also just talk in plain English.

| In app | Type this | What it does (simple) |
|--------|-----------|------------------------|
| ACC setup | `$setup` | First-time setup for this project |
| ACC home | `$orchestrator` | Front door — helps pick the next step |
| ACC help | `$help` | “Where am I?” in plain language |
| ACC status | `$status` | Current task and what’s next |
| ACC resume | `$resume` | Continue after a break |
| ACC check | `$verify` | Check the work with proof |
| ACC fix | `$fix` | Help when the same thing keeps failing |

---

## More skills (optional)

| In app | Type this | What it does |
|--------|-----------|-------------|
| ACC start | `$onboard` | Idea / existing project / bug starting points |
| ACC clarify | `$clarify` | Only the questions needed to unblock you |
| ACC plan | `$plan` | Ordered task plan |
| ACC build | `$execute` | Build from the plan |
| ACC learn | `$learn` | Save a lesson to memory |
| ACC note | `$capture` | Record a decision or blocker |
| ACC scope | `$govern` | Guard against silent scope change |
| ACC clear | `$readable` | Keep work understandable |
| ACC plugins | `$bridge` | Play nice with other plugins |
| ACC usage | `$usage` | Token usage view |
| ACC settings | `$settings` | Preferences |
| ACC update | `$update` | After a plugin upgrade |
| ACC handoff | `$handoff` | Pass work to a later session |

---

## Memory (short)

- Durable memory = linked Markdown files  
- Recalled before questions, plans, and actions  
- Advises — never decides alone  
- Viewer optional (e.g. Obsidian); ACC works without one  

Details: [`MEMORY-CONTRACT.md`](MEMORY-CONTRACT.md)

---

## Automations

Optional read-only Codex Desktop schedules (daily recap, stuck nudge, weekly memory digest): [`automations/`](automations/README.md)

---

## Tests

Run the suite locally (CI runs the same path):

```powershell
python -m pytest plugins/anyone-can-code/tests -q
```

Do not hardcode pass counts in docs — trust CI and the command above.

---

## Safeguards

ACC enforces `mechanics_docs_gate` before any platform mechanics work — hooks, plugin runtime, Windows launch, MCP, or tool-plumbing changes require a docs brief from official docs/source before code is written. When official docs are missing, controlled proof plus recorded uncertainty is required. This blocks silent assumptions about platform mechanics.

---

## Deeper docs

| Doc | For |
|-----|-----|
| [Root README](../../README.md) | Install + everyday commands |
| [docs/README](../../docs/README.md) | Map of all repo docs |
| [`IMPLEMENTATION-SOURCE-OF-TRUTH.md`](IMPLEMENTATION-SOURCE-OF-TRUTH.md) | What shipped |
| [`VALIDATION.md`](VALIDATION.md) | Acceptance checklist |
| [`MEMORY-CONTRACT.md`](MEMORY-CONTRACT.md) | Memory rules |
| [CONTRIBUTING](../../.github/CONTRIBUTING.md) | How to contribute |
| [Privacy](../../docs/PRIVACY.md) · [Terms](../../docs/TERMS.md) | Legal |

---

<p align="center">
  <sub>MIT · Built by <a href="https://github.com/mitunmanav">Mitun</a> · <a href="https://anyone-can-code.vercel.app/">anyone-can-code.vercel.app</a></sub>
</p>
