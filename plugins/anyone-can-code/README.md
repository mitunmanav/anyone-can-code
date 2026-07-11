<p align="center">
  <img src="assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>You describe what you want.</strong><br/>
  Idea → plan → build → verify. Codex plugin for Windows. No engineering background required.
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

Full install guide: [root README](../../README.md). Short version:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Then: Codex → plugin browser → **Anyone Can Code** → Install → restart → open a project → `$setup`.

**Current version:** see [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) (also on [Releases](https://github.com/mitunmanav/anyone-can-code/releases)).

---

## Skills

| Skill | What it does |
|-------|-------------|
| `$setup` | First-use bootstrap |
| `$orchestrator` | Front door — detects starting point and routes |
| `$onboard` | Idea / spec / existing repo / bug |
| `$clarify` | Only the questions needed to unblock |
| `$plan` | Ordered task plan |
| `$execute` | Build from the plan; update state |
| `$verify` | Evidence-first completion check |
| `$fix` | Recovery when something keeps failing |
| `$resume` | Continue after interrupt or restart |
| `$status` | Where things stand |
| `$help` | Project state in plain language |
| `$learn` | Save a lesson to Markdown memory |
| `$capture` | Record a decision, blocker, or insight |
| `$govern` | Guard against silent scope change |
| `$readable` | Keep code and artifacts understandable |
| `$bridge` | Detect other plugins; route safely |
| `$usage` | Token usage dashboard |
| `$settings` | Persona, verbosity, automation |
| `$update` | Migrate state after plugin upgrade |
| `$handoff` | Structured session handoff |

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
