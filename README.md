<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h3 align="center">Anyone Can Code</h3>
<p align="center">
  A Codex plugin that takes you from idea to verified result — no engineering background required.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-anyone--can--code.vercel.app-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/6EcuDzJS"><img src="https://img.shields.io/badge/Discord-join%20community-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://anyone-can-code.vercel.app/#waitlist"><img src="https://img.shields.io/badge/waitlist-join%20now-FF6B35?style=flat-square" alt="Waitlist"/></a>
  <img src="https://img.shields.io/badge/tests-158%20passing-brightgreen?style=flat-square" alt="Tests"/>
  <img src="https://img.shields.io/badge/platform-Codex%20Windows-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/>
</p>

---

## What it does

You describe what you want. Anyone Can Code handles the rest.

- Routes your starting point automatically — idea, bug, feature, review, or ship
- Asks only the questions needed to unblock you
- Remembers decisions across sessions using portable Markdown memory
- Verifies work before claiming it done — no silent success claims
- Windows-first, built for Codex Desktop

```
You:  "I want to build a website with auth and payments"

ACC:  Detected: idea + website
      Relevant memory used: 1 item
      Route: intake → checklist → plan
      Plan: website + auth + Stripe. SEO later.
```

---

## Install

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Restart Codex, open a project, run `$setup`.

**Requirements:** Codex Desktop · Windows · Python

---

## Skills

| Skill | What it does |
|-------|-------------|
| `$orchestrator` | Front door — detects your starting point and routes |
| `$clarify` | Asks only the questions needed to unblock |
| `$plan` | Turns a clear request into an ordered task plan |
| `$execute` | Builds from the task plan, updates workflow state |
| `$verify` | Evidence-first completion check |
| `$resume` | Picks up after interruption or restart |
| `$learn` | Saves a lesson to portable Markdown memory |
| `$status` | Where things stand right now |
| `$settings` | Persona, verbosity, automation level |
| `$update` | Migrates project state after plugin upgrade |

---

## Tests

**158 passing · 3 skipped (Windows shell) · 0 failures**

| Suite | Tests | Covers |
|-------|-------|--------|
| `test_project_state` | 74 | State, setup, update, memory migration, rollback, safety receipts |
| `test_front_door` | 40 | Routing, specialist containment, ownership contract, bridge |
| `test_memory_backend` | 13 | Markdown memory store, recall, deduplication |
| `test_status_model` | 11 | State vocabulary, verification claims, visual QA guards |
| `test_git_workflow` | 7 | Git guardrails, branch/commit/PR rules |
| `test_product_intake` | 6 | Intake questions, checklist generation, plan line |
| `test_memory_preflight` | 4 | Memory recall before first action |

```powershell
python -m unittest discover -s plugins/anyone-can-code/tests
```

---

## Community

| | |
|---|---|
| 🌐 Website | [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) |
| 💬 Discord | [discord.gg/6EcuDzJS](https://discord.gg/6EcuDzJS) — builders welcome |
| 📋 Waitlist | [anyone-can-code.vercel.app/#waitlist](https://anyone-can-code.vercel.app/#waitlist) |
| 🐛 Bugs | [GitHub Issues](https://github.com/mitunmanav/anyone-can-code/issues) |

---

## Repo layout

```
plugins/anyone-can-code/     plugin source (skills, hooks, scripts, assets)
.agents/plugins/             marketplace definition
.github/workflows/           release packaging
CHANGELOG.md                 release history
CONTRIBUTING.md              contribution guide
```

---

<p align="center">MIT License · Built by <a href="https://github.com/mitunmanav">Mitun</a></p>
