# Security

## Report a vulnerability

Use a **private** [GitHub security advisory](https://github.com/mitunmanav/anyone-can-code/security/advisories/new).

Do **not** post exploits or sensitive details in public issues.

Include:

- Plugin version (from `plugins/anyone-can-code/.codex-plugin/plugin.json` or Releases)
- Steps to reproduce
- Logs with secrets removed

## Local data

Anyone Can Code keeps project state under `.codex/anyone-can-code/` and may use the user Codex home for runtime memory. That is local user data — **do not commit it**.

See [PRIVACY.md](../docs/PRIVACY.md) for what is stored and what is not.

## Scope

This project is a local workflow plugin for Codex Desktop. Security reports about Codex itself or third-party services should go to those vendors; report here only issues in this repository’s plugin, scripts, hooks, or docs.
