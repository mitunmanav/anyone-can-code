<p align="center">
  <img src="assets/logo.png" alt="Anyone Can Code" width="420"/>
</p>

<h1 align="center">Anyone Can Code</h1>

<p align="center">
  <strong>Reliability workflow plugin for OpenAI Codex (Desktop + CLI).</strong><br/>
  Say what you want. ACC helps Codex plan it, build it, and prove it works.<br/>
  <em>One plugin for both hosts.</em>
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

**New here?** [First day guide](../../docs/FIRST_DAY.md) · Full install: [root README](../../README.md)  

**Install GIF (in this repo):** [docs/media/install-setup.gif](../../docs/media/install-setup.gif)  
**Full video:** [docs/media/install-setup.mp4](../../docs/media/install-setup.mp4) · [website player](https://anyone-can-code.vercel.app/#install)  

**Stuck?** [Start here](https://github.com/mitunmanav/anyone-can-code/discussions/5) · [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9)

### Install (short)

**One plugin** for Desktop app and CLI.

**Desktop:** marketplace URL → install **Anyone Can Code** → trust hooks → restart → `$setup`  

**CLI:** `codex plugin marketplace add mitunmanav/anyone-can-code --ref main` → `/plugins` install **Anyone Can Code** → `/hooks` trust → `$setup`  
**CLI auto memory:** yes when hooks trusted (same as Desktop). `$learn` / `$wiki` optional.

**Current version:** **v2.0.0-beta.5** ([plugin.json](.codex-plugin/plugin.json)) · [Releases](https://github.com/mitunmanav/anyone-can-code/releases)

### If install fails

| What you see | What to try |
|--------------|-------------|
| Marketplace not found / add fails | Paste the **full** GitHub URL: `https://github.com/mitunmanav/anyone-can-code` — not a short name |
| Plugin missing after restart | Re-open Plugins, confirm **Anyone Can Code** is installed and **on** |
| Installed but nothing works | Hooks → enable + **trust every ACC hook** → restart / new chat |
| `$setup` no reply | Open a **project folder**, start a **new chat**, run `$setup` again |

More: [FAQ](https://github.com/mitunmanav/anyone-can-code/discussions/9) · [Install issue form](https://github.com/mitunmanav/anyone-can-code/issues/new?template=install_problem.yml) · [root troubleshooting](../../README.md#if-something-fails)

### Safety (hooks)

Built from [Codex hooks docs](https://developers.openai.com/codex/hooks):

- **Trust hooks** or ACC cannot guard or save memory.
- Blocks dangerous shell patterns (force-push, wipe-disk style, download-to-shell).
- Hard deploy/publish runs a local security checklist (open signup, default passwords, placeholder secrets).
- Safe read/test commands can auto-allow; multi-step or risky chains still ask you.
- If a safety hook crashes, it **blocks** instead of quietly allowing (fail closed).
- Hooks cover **Bash / apply_patch / MCP** only — not every shell path. Keep Codex sandbox on.

Memory stays **on your machine** under `.codex/anyone-can-code/memory/`.

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
| ACC wiki | `$wiki` | Save, ask, or clean project notebook (ACC only; no Codex native memory) |
| ACC note | `$capture` | Record a decision or blocker |
| ACC scope | `$govern` | Guard against silent scope change |
| ACC clear | `$readable` | Keep work understandable |
| ACC plugins | `$bridge` | Play nice with other plugins |
| ACC usage | `$usage` | Token usage view |
| ACC settings | `$settings` | Preferences |
| ACC update | `$update` | After a plugin upgrade |
| ACC handoff | `$handoff` | Pass work to a later session |
| ACC approval mode | `$approval-mode` | ACC soft allow grades (not Codex /permissions) |
| ACC repo map | `$repo-map` | Ranked repo map sample; thin SessionStart inject |
| ACC tool budget | `$tool-budget` | Soft tool-call budget warn (never deny) |
| ACC auto lint | `$auto-lint` | Soft after-edit lint/test hint (opt-in) |
| ACC you-brain | `$you-brain` | Mine past sessions into a YOU preview (apply only on yes) |
| ACC council | `$council` | Multi-view check (not a ship gate — still `$verify`) |
| ACC skeptic | `$skeptic` | Read-only adversarial review of a diff (not $verify) |
| ACC parallel fix | `$parallel-fix` | One file per subagent when many tests fail |
| ACC roster | `$roster` | Named subagent roster for parallel work |
| ACC strong run | `$oneshot` | One-shot checklist before a big run |
| ACC checkpoint | `$checkpoint` | File checkpoints (ACC files, not a shadow git) |
| ACC rule suggest | `$rule-suggest` | Suggest a durable rule when the same fix repeats |
| ACC cost guard | `$cost-guard` | Soft Luna/Terra/Sol tips (you pick the model) |
| ACC bite plan | `$bite-plan` | 2–5 min checkbox steps |
| ACC memory hygiene | `$memory-hygiene` | Age notes, flag secrets, block full-chat dumps |
| ACC efficiency | `$efficiency` | Lean inject + soft cheaper-model tip (never force picker) |
| ACC plan gate | `$plan-gate` | PLAN.md steps + GO before product writes |
| ACC ledger | `$ledger` | Progress board (WHERE / NEXT / DONE / OPEN) |

---

## Desktop & CLI

One plugin. **Same** on both (hooks trusted): auto memory, skills, plan → build → check, safety.

**Differs:** trust/install path; Scheduled + Sites = Desktop only.

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
