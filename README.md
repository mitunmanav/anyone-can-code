<p align="center">
  <img src="plugins/anyone-can-code/assets/logo.png" alt="Anyone Can Code" width="280"/>
</p>

<h3 align="center">Anyone Can Code</h3>
<p align="center">
  You describe what you want. It plans, builds, and verifies — no engineering background required.
</p>

<p align="center">
  <a href="https://anyone-can-code.vercel.app/"><img src="https://img.shields.io/badge/website-anyone--can--code.vercel.app-10A37F?style=flat-square" alt="Website"/></a>
  <a href="https://discord.gg/qgS29y7TqP"><img src="https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://github.com/mitunmanav/anyone-can-code/releases"><img src="https://img.shields.io/github/v/release/mitunmanav/anyone-can-code?include_prereleases&style=flat-square&label=release" alt="Release"/></a>
  <img src="https://img.shields.io/badge/tests-363%20passing-brightgreen?style=flat-square" alt="Tests"/>
  <img src="https://img.shields.io/badge/platform-Codex%20Windows-0078D4?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" alt="Beta"/>
</p>

---

## Quick start

**Need:** [Codex Desktop](https://openai.com/codex/) · Windows · Python

**1. Add the marketplace** (paste in terminal):

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

**2. Install the plugin**  
Codex → plugin browser → **Anyone Can Code** → Install → restart Codex.

**3. First project**  
Open a folder, start a chat, run:

```
$setup
```

Then say what you want in plain English, or run `$orchestrator`.

```
You:  "I want a website with login and payments"

ACC:  Detected idea · website
      Plan: site + auth + Stripe. SEO later.
```

---

## Everyday commands

| Say this | What happens |
|----------|----------------|
| `$setup` | First-time project setup |
| `$orchestrator` | Front door — picks the right path |
| `$help` | Plain-language “where am I?” |
| `$status` | Current task and next step |
| `$resume` | Continue after a break |
| `$verify` | Check work with evidence |
| `$fix` | Recover when something keeps failing |

More skills (plan, execute, memory, settings…): [plugin README](plugins/anyone-can-code/README.md).

---

## What you get

- Routes idea / bug / feature / review / ship automatically  
- Asks only questions that unblock you  
- Remembers decisions in portable Markdown  
- Verifies before claiming “done”  
- Optional background automations: [automations/](plugins/anyone-can-code/automations/README.md)

---

## Help

| | |
|---|---|
| Website | [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/) |
| Discord | [discord.gg/qgS29y7TqP](https://discord.gg/qgS29y7TqP) |
| Bugs / ideas | [GitHub Issues](https://github.com/mitunmanav/anyone-can-code/issues) |
| Security | [SECURITY.md](.github/SECURITY.md) — private reports only |
| Contributing | [CONTRIBUTING.md](.github/CONTRIBUTING.md) |

---

## Repo map

```
plugins/anyone-can-code/   plugin (skills, hooks, scripts, tests)
.agents/plugins/           marketplace definition
.github/                   issues, PR template, CI, community docs
docs/                      privacy, terms, credits
CHANGELOG.md               release history
```

Tests: `python -m pytest plugins/anyone-can-code/tests -q`

---

<p align="center">MIT · Built by <a href="https://github.com/mitunmanav">Mitun</a></p>
