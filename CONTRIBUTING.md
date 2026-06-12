# Contributing

Thanks for helping improve Anyone Can Code.

This project is meant to stay practical, Windows-friendly, and evidence-first. Contributions should make the plugin easier to install, understand, use, recover, or verify.

## Project Model

Mitun is the creator and product owner. He is building a practical Codex workflow tool with AI-assisted development and wants technical contributors to help make the engineering solid.

This repository is set up for public collaboration: GitHub Issues receive external bugs and ideas, pull requests carry improvements, validation checks protect quality, and releases publish packaged versions. Internal product work is tracked in Linear project `Anyone Can Code`.

That means contributions are especially welcome in:

- plugin architecture
- Python quality and maintainability
- MCP memory behavior
- Windows setup and update flows
- AI workflow design and prompt quality
- testing, validation, and release process
- documentation for non-technical users

Please explain technical choices plainly. A good contribution should improve the project and help the maintainer understand what changed.

## Ground Rules

- Keep changes focused and easy to review.
- Prefer clear docs and small fixes over broad rewrites.
- Develop on a feature branch or development worktree, never directly on `main`.
- Test committed candidates in the testing worktree before pushing them to GitHub.
- Publish and release only from stable `main`.
- Do not commit local runtime state, user memory, logs, or generated project data.
- Keep public docs free of private machine paths, personal tokens, and private screenshots.
- Validate claims before marking work complete.

See `DEVELOPMENT-WORKFLOW.md` for tracker, worktree, pull request, and release roles.

## Local Checks

Run these checks before opening a pull request:

```powershell
python plugins\anyone-can-code\scripts\doctor.py --json
python -m py_compile plugins\anyone-can-code\mcp\server.py plugins\anyone-can-code\hooks\scripts\state.py plugins\anyone-can-code\hooks\scripts\guard.py plugins\anyone-can-code\hooks\scripts\audit.py plugins\anyone-can-code\hooks\scripts\load_session.py plugins\anyone-can-code\hooks\scripts\save_session.py plugins\anyone-can-code\scripts\setup.py plugins\anyone-can-code\scripts\update.py plugins\anyone-can-code\scripts\doctor.py plugins\anyone-can-code\scripts\codeburn.py plugins\anyone-can-code\scripts\token-dashboard.py
python -m json.tool plugins\anyone-can-code\.codex-plugin\plugin.json
python -m json.tool plugins\anyone-can-code\.mcp.json
python -m json.tool .agents\plugins\marketplace.json
```

## Pull Requests

Good pull requests include:

- A short description of the user-facing change.
- The reason the change is needed.
- A plain-language explanation of technical tradeoffs.
- The checks you ran.
- Any known limitations or follow-up work.

## Release Changes

For release changes:

1. Update `plugins/anyone-can-code/.codex-plugin/plugin.json`.
2. Update `CHANGELOG.md`.
3. Push a matching tag, such as `v1.0.1`.

The release workflow validates that the tag matches the plugin manifest version.
