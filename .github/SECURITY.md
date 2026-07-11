# Security

## Report a vulnerability

**Private only** — [open a GitHub security advisory](https://github.com/mitunmanav/anyone-can-code/security/advisories/new).

Do **not** post exploits, tokens, or sensitive details in public Issues or Discussions.

### What to include

- Plugin version (`plugins/anyone-can-code/.codex-plugin/plugin.json` or [Releases](https://github.com/mitunmanav/anyone-can-code/releases))
- Steps to reproduce
- Impact (what an attacker could do)
- Logs with secrets removed

### Response path

1. Advisory is private by default.  
2. Maintainer acknowledges when possible.  
3. Fix ships in a release when ready; credit if you want it.

Not a security issue? Use [Issues](https://github.com/mitunmanav/anyone-can-code/issues/new/choose), [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions), or [Discord](https://discord.gg/qgS29y7TqP) instead.

## Local data

Anyone Can Code keeps project state under `.codex/anyone-can-code/` and may use the user Codex home for runtime memory. That is local user data — **do not commit it**.

See [PRIVACY.md](../docs/PRIVACY.md) for what is stored and what is not.

## Scope

This project is a local workflow plugin for Codex Desktop. Security reports about Codex itself or third-party services should go to those vendors; report here only issues in this repository’s plugin, scripts, hooks, or docs.
