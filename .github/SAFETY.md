# Safety guide (plain English)

You do not need to be technical. Follow this so the public repo stays safer.

## What protects you already

| Guard | What it does |
|-------|----------------|
| **Secret scanning** | Blocks known API keys / tokens from being pushed |
| **Push protection** | Stops a push if it looks like a secret |
| **Dependabot** | Opens PRs when GitHub Actions need security updates |
| **CodeQL** | Weekly + on PR scan for common code bugs |
| **CI validate** | Tests + doctor must pass on PRs to `main` |
| **Agent guard** | Can pause outside AI coding bots when you focus |
| **Issue / PR AI briefs** | Plain English summary before you dig in |
| **No wiki / projects** | Less attack surface |
| **Private security reports** | People report vulns privately, not in public issues |

## Rules for you (simple)

1. **Never paste passwords, tokens, or API keys** into Issues, Discussions, PRs, or commits.  
2. **Never commit** files named `.env`, keys, or folders with your private chat history.  
3. **Only merge PRs** after green checks and after you (or AI brief) understand what changed.  
4. **Do not give write access** to strangers. Collaborators = people you trust.  
5. **Use 2FA** on your GitHub account (Settings → Password and authentication).  
6. **Turn maintainer focus ON** when working hard: Actions → **Agent guard** → Run → `true`.  
7. **Security problems** → [private advisory](https://github.com/mitunmanav/anyone-can-code/security/advisories/new), not public Issues.

## If something looks wrong

| Sign | Do this |
|------|---------|
| Random PR from stranger with weird code | Do **not** merge. Close if spam. |
| Comment asks you to run a secret command | Ignore. Report if threatening. |
| Dependabot PR | Usually safe to review; still check CI green. |
| Email “urgent security, click this link” | Go to GitHub Security tab yourself — don’t click cold links. |

## Local plugin data

ACC stores project notes under `.codex/anyone-can-code/` on **your machine**. That stays local. Do not upload that folder to GitHub.

## More detail

- [SECURITY.md](SECURITY.md) — how to report vulnerabilities  
- [MAINTAINER.md](MAINTAINER.md) — maintainer focus + AI agents  
- [CONTRIBUTING.md](CONTRIBUTING.md) — who may contribute  
