<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="320"/>
</p>

<h3 align="center">Anyone Can Code</h3>
<p align="center">
  A Codex plugin that takes you from idea to verified result — no engineering background required.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-anyone--can--code.vercel.app-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join%20community-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://anyone-can-code.vercel.app/#waitlist"><img src="https://img.shields.io/badge/waitlist-join%20now-FF6B35?style=flat-square" alt="Waitlist"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/stargazers"><img src="https://img.shields.io/github/stars/mitunmanav/anyone-can-code?style=flat-square&color=yellow" alt="Stars"/></a>
  <img src="https://img.shields.io/badge/tests-194%20passing-brightgreen?style=flat-square" alt="Tests"/>
  <img src="https://img.shields.io/badge/platform-Codex%20Windows-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" alt="Beta"/>
  <a href="https://github.com/mitunmanav/anyone-can-code/commits/main"><img src="https://img.shields.io/github/last-commit/mitunmanav/anyone-can-code?style=flat-square" alt="Last commit"/></a>
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

Copy-paste one line into your terminal:

```powershell
codex plugin marketplace add https://github.com/mitunmanav/anyone-can-code
```

Or use the GitHub shorthand:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Then open the Codex plugin browser, pick **Anyone Can Code**, click install. Restart Codex, open a project, run `$setup`.

**Requirements:** Codex Desktop · Windows · Python

---

## Skills

| Skill | What it does |
|-------|-------------|
| `$orchestrator` | Front door — detects your starting point and routes |
| `$onboard` | Figures out if you start from an idea, spec, repo, or bug |
| `$clarify` | Asks only the questions needed to unblock |
| `$plan` | Turns a clear request into an ordered task plan |
| `$execute` | Builds from the task plan, updates workflow state |
| `$verify` | Evidence-first completion check |
| `$fix` | Recovery workflow when something keeps failing |
| `$resume` | Picks up after interruption or restart |
| `$learn` | Saves a lesson to portable Markdown memory |
| `$capture` | Records a decision, blocker, or insight on request |
| `$status` | Where things stand right now |
| `$help` | Explains the current project state in plain language |
| `$govern` | Guards against silent scope changes |
| `$readable` | Keeps code and artifacts understandable |
| `$bridge` | Detects other installed plugins and routes to them safely |
| `$usage` | Token usage dashboard — zero tokens spent |
| `$settings` | Persona, verbosity, automation level |
| `$setup` | Bootstraps project-local state on first use |
| `$update` | Migrates project state after plugin upgrade |

---

## Automations

Ready-made background tasks you paste into Codex Desktop's Automations pane: daily project recap, stuck-task nudge, weekly memory digest. All read-only, no installs. See [`plugins/anyone-can-code/automations/`](plugins/anyone-can-code/automations/README.md).

---

## Tests

**194 passing · 3 skipped (Windows shell) · 0 failures**

Coverage spans routing and plugin containment, transactional state with rollback, Markdown memory with read/write proof, doctor integrity checks (plugin cache drift, missing skills), a circuit breaker for repeated failures, model-choice ledger, product intake, git guardrails, skill contracts, and a full-system smoke test.

```powershell
pip install pytest
python -m pytest plugins/anyone-can-code/tests -q
```

---

## Community

| | |
|---|---|
| 🌐 Website | [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) |
| 💬 Discord | [discord.gg/qgS29y7TqP](https://discord.gg/qgS29y7TqP) — builders welcome |
| 📋 Waitlist | [anyone-can-code.vercel.app/#waitlist](https://anyone-can-code.vercel.app/#waitlist) |
| 🐛 Bugs | [GitHub Issues](https://github.com/mitunmanav/anyone-can-code/issues) |

---

## Star History

<a href="https://star-history.com/#mitunmanav/anyone-can-code&Date">
  <img src="https://api.star-history.com/svg?repos=mitunmanav/anyone-can-code&type=Date" alt="Star History Chart" width="600"/>
</a>

---

## Repo layout

```
plugins/anyone-can-code/     plugin source (skills, hooks, scripts, assets)
.agents/plugins/             marketplace definition
.github/workflows/           release packaging
.github/CONTRIBUTING.md      contribution guide
.github/CODE_OF_CONDUCT.md   community guidelines
.github/SECURITY.md          vulnerability reporting
.github/SUPPORT.md           where to get help
docs/                        privacy, terms, credits, operating contract
CHANGELOG.md                 release history
```

---

<p align="center">MIT License · Built by <a href="https://github.com/mitunmanav">Mitun</a></p>
