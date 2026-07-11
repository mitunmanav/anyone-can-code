# Contributing

Thanks for helping Anyone Can Code.

Goal: keep it practical, Windows-friendly, and evidence-first — easier to install, understand, use, recover, or verify.

## Welcome help

- Plugin architecture and Python quality  
- Windows setup / update flows  
- Memory (Markdown MCP) behavior  
- Workflow design and prompts  
- Tests, validation, release process  
- Docs for non-technical users  

Explain technical choices in plain language so a non-expert maintainer can review them.

## Rules

- Small, focused changes. Feature branch — not direct `main`.  
- No local runtime state, user memory, logs, or secrets in commits.  
- Validate before claiming done.  
- Full workflow: `DEVELOPMENT-WORKFLOW.md`.

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

## Releases

1. Bump `plugins/anyone-can-code/.codex-plugin/plugin.json` version.  
2. Update `CHANGELOG.md`.  
3. Tag matching version (e.g. `v1.1.0-beta.3`).  

Release CI checks tag ↔ manifest version.
