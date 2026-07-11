<p align="center">
  <img src="assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>You describe what you want in plain English.</strong><br/>
  Idea → plan → build → verify. Codex plugin for Windows. No programming background required.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-live-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/mitunmanav/anyone-can-code/validate.yml?branch=main&style=flat-square&label=CI" alt="CI"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/platform-Codex%20·%20Windows-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" alt="Beta"/>
</p>

**New here?** Full install (with hooks): [root README — How to install](../../README.md#how-to-install)  

**Install video (in this repo):** [docs/media/install-setup.mp4](../../docs/media/install-setup.mp4) · captions: [install-setup.vtt](../../docs/media/install-setup.vtt)  
**Also on the website:** [anyone-can-code.vercel.app/#install](https://anyone-can-code.vercel.app/#install)  

**Stuck?** [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5) · [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)

### Install (short)

1. Copy `https://github.com/mitunmanav/anyone-can-code`  
2. Codex → **Plugins** → **+** → **Add a Marketplace** → paste URL  
3. Scroll → **Anyone Can Code** → **Install**  
4. **Hooks → Settings → enable + trust every ACC hook** (required; not automatic)  
5. Restart Codex · enable tools · open a project · `$setup` · say what you want  

Optional terminal: `codex plugin marketplace add mitunmanav/anyone-can-code --ref main` — then still do steps 3–5.

**Current version:** [plugin.json](.codex-plugin/plugin.json) · [Releases](https://github.com/mitunmanav/anyone-can-code/releases)

---

## Everyday commands (start here)

Type these in the Codex chat. You can also just talk in plain English.

| Type this | What it does (simple) |
|-----------|------------------------|
| `$setup` | First-time setup for this project |
| `$orchestrator` | Front door — helps pick the next step |
| `$help` | “Where am I?” in plain language |
| `$status` | Current task and what’s next |
| `$resume` | Continue after a break |
| `$verify` | Check the work with proof |
| `$fix` | Help when the same thing keeps failing |

---

## More skills (optional)

| Skill | What it does |
|-------|-------------|
| `$onboard` | Idea / existing project / bug starting points |
| `$clarify` | Only the questions needed to unblock you |
| `$plan` | Ordered task plan |
| `$execute` | Build from the plan |
| `$learn` | Save a lesson to memory |
| `$capture` | Record a decision or blocker |
| `$govern` | Guard against silent scope change |
| `$readable` | Keep work understandable |
| `$bridge` | Play nice with other plugins |
| `$usage` | Token usage view |
| `$settings` | Preferences |
| `$update` | After a plugin upgrade |
| `$handoff` | Pass work to a later session |

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
