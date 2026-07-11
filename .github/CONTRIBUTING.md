# Contributing

Thanks for helping Anyone Can Code.

Goal: practical, Windows-friendly, evidence-first — easier to install, understand, use, recover, or verify.

Product site: [anyone-can-code.vercel.app](https://anyone-can-code.vercel.app/)  
Docs map: [docs/README.md](../docs/README.md)

## Who can contribute

| Who | Policy |
|-----|--------|
| Outside **humans** | Always welcome |
| Outside **AI coding agents** | Welcome **except** when maintainer focus is ON |
| Maintainer (Mitun) | Owns product decisions |

### Maintainer focus

When the open issue labeled `maintainer-working` exists (or `MAINTAINER_WORKING=true`):

- Outside **AI agents / coding bots** must not open or update PRs — they are auto-closed.
- Outside **humans** may still open small PRs (review may be slower).

Focus is temporary so Mitun can work without agent noise. Details: [MAINTAINER.md](MAINTAINER.md).

## Help we want

- Plugin architecture and Python quality  
- Windows setup / update flows  
- Memory (Markdown MCP) behavior  
- Workflow design and prompts  
- Tests, validation, release process  
- Docs for non-technical users  

Explain technical choices in **plain language** so a non-expert maintainer can review.

AI reviews every issue/PR and posts a maintainer brief — write so that brief stays accurate.

## Rules

- Small, focused changes. Feature branch — never force-push `main`.  
- Open a PR. Wait for **Validate** CI (and the AI maintainer brief).  
- No local runtime state, user memory, logs, or secrets in commits.  
- Validate before claiming done.  
- Full workflow: [DEVELOPMENT-WORKFLOW.md](../DEVELOPMENT-WORKFLOW.md).

## Checks before a PR

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
python -m pytest plugins\anyone-can-code\tests -q
python -m json.tool plugins\anyone-can-code\.codex-plugin\plugin.json
python -m json.tool .agents\plugins\marketplace.json
```

Also compile-check any Python files you touched.

## Pull requests

Include: what changed for users, why, checks you ran, known limits.

If you used an AI agent to write the PR, say so in the description (one line).

## Issues

- Bugs / features: GitHub Issues (templates).  
- Questions: [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) or [Discord](https://discord.gg/qgS29y7TqP).  
- Security: private advisory only — see [SECURITY.md](SECURITY.md).

Every issue gets an automatic plain-language AI brief for the maintainer.  
Re-run: comment `/ai-review`.

## Releases (maintainers)

1. Bump `plugins/anyone-can-code/.codex-plugin/plugin.json` version.  
2. Update [CHANGELOG.md](../CHANGELOG.md).  
3. Tag matching version (e.g. `v1.1.0-beta.3`).  

Release CI checks tag ↔ manifest version. Install line for users:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```
