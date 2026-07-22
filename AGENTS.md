# Anyone Can Code — agent context (public)

Product-facing notes only. Process / learning notes do **not** belong in this repo.

## Product

- **Name:** Anyone Can Code (ACC)
- **Version:** see `plugins/anyone-can-code/.codex-plugin/plugin.json` (v2.0.0-beta.5, one plugin)
- **Platform:** Codex Desktop + Codex CLI (one install)
- **Memory:** Desktop + CLI auto memory when hooks trusted. Optional `$learn` / `$wiki`.
- **Site:** https://anyone-can-code.vercel.app/
- **Repo:** https://github.com/mitunmanav/anyone-can-code

## Install (truth)

**One plugin** for Desktop and CLI (Superpowers-style).

### Desktop
1. Codex → Plugins → **+** → Add a Marketplace → paste `https://github.com/mitunmanav/anyone-can-code`
2. Install **Anyone Can Code**
3. Enable + **trust every ACC hook** (required)
4. Restart Codex
5. Open a project → `$setup` → say what you want

### CLI
1. `codex plugin marketplace add mitunmanav/anyone-can-code --ref main`
2. `/plugins` → install **Anyone Can Code**
3. `/hooks` → trust every ACC hook
4. New thread → `$setup`

## Architecture

```
plugins/anyone-can-code/   # one plugin (Desktop + CLI)
.agents/plugins/           # marketplace.json (one entry)
.github/                   # community + CI
docs/                      # privacy, terms, credits, media, docs map
```

Runtime state: `.codex/anyone-can-code/` (local, not committed).

## Rules for agents in this repo

- Non-technical users first. Plain English in public docs.
- Small polish only — no redesigns of product surface without ask.
- Evidence before “done”. Run tests / doctor when you touch plugin code.
- No secrets in commits, issues, or discussions.
- Security findings: tell maintainer **privately** — never public Issues/Discussions/PoCs.
- Do not push / tag / release unless the user explicitly asks.

## Checks

```bash
python3 -m pytest plugins/anyone-can-code/tests -q
python3 plugins/anyone-can-code/scripts/doctor.py --json
python3 -m json.tool plugins/anyone-can-code/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

## More

- User install: [README.md](README.md)
- Docs map: [docs/README.md](docs/README.md)
- Contributing: [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)
