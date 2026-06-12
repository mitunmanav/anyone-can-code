# Anyone Can Code

Anyone Can Code is a Windows-first Codex plugin marketplace for builders who want a clearer path from idea to verified result.

It is started by Mitun, a builder using AI-assisted development to make software creation more approachable for people with ideas, taste, and persistence, even if they do not yet have deep engineering experience.

## Project Status

Anyone Can Code is at its first public release candidate. The initial public version is `1.0.0`.

## Current Release

- Version: `1.0.0`
- Release tag: `v1.0.0`
- License: MIT

## What It Does

- Routes rough ideas, existing repos, bugs, polish work, and release tasks through one front door.
- Uses focused skills for clarification, planning, implementation, verification, recovery, settings, and usage.
- Keeps completion evidence-first, so "built" and "verified" do not get blurred together.
- Stores durable workflow learnings locally through the bundled MCP memory server.
- Supports optional hooks for workflow signals when users explicitly enable them.

## Creator and Contributor Model

Mitun is the creator, product owner, and day-to-day maintainer of the project. This GitHub repository is set up as the public home for the plugin: issues for bugs and ideas, pull requests for improvements, validation checks for quality, and releases for packaged versions.

The project needs technical contributors who can help with:

- Codex plugin architecture and marketplace packaging
- Python scripts, MCP memory behavior, and local state handling
- Windows compatibility and setup reliability
- AI workflow design, prompt quality, and verification patterns
- Documentation that makes technical ideas usable for non-technical people
- Testing, security review, and release quality

If you are technical and want to help, the best contributions are practical fixes, clear explanations, and small improvements that make the plugin safer and easier to use.

## Install

Add this repository as a Codex plugin marketplace:

```powershell
codex plugin marketplace add mitunmanav/anyone-can-code --ref main
```

Then install **Anyone Can Code** from the Codex plugin browser, restart Codex, open a project, and run:

```text
$setup
```

## Requirements

- Codex Desktop with plugin marketplaces enabled
- Windows-first runtime environment
- Python available as `python` for bundled scripts and the MCP memory server

## Main Skills

- `$orchestrator` routes the request.
- `$clarify` collects missing requirements only when needed.
- `$plan` turns uncertainty into a practical path.
- `$execute` carries out the work.
- `$verify` checks evidence before completion.
- `$resume` restores interrupted work.
- `$status`, `$settings`, `$usage`, and `$update` keep the workflow maintainable.

## Repository Layout

- `/.agents/plugins/marketplace.json` - marketplace definition
- `/plugins/anyone-can-code` - plugin source bundle
- `/.github/workflows/release.yml` - release packaging workflow
- `/CHANGELOG.md` - release history
- `/CONTRIBUTING.md` - contribution guide

## Star History

Star history will be available after the repository is public:

https://www.star-history.com/#mitunmanav/anyone-can-code&Date

## Support

- Open an issue for reproducible bugs or feature requests.
- Open a technical help issue if you want to improve architecture, AI behavior, testing, or release quality.
- For security issues, follow `SECURITY.md`.
- For contribution expectations, follow `CONTRIBUTING.md`.

## Releasing

Releases are automated with GitHub Actions.

1. Update the plugin version in `./plugins/anyone-can-code/.codex-plugin/plugin.json`.
2. Commit and push the change.
3. Create and push a matching semantic version tag, for example `v1.0.0`.
4. GitHub Actions packages `plugins/anyone-can-code` as a zip and publishes the release assets.

## Development

Project workflow:

- Linear tracks product work and priorities.
- Flow-Next stores local implementation specs and verification evidence.
- Development and testing happen in separate local Git worktrees.
- Verified branches are pushed to GitHub and merged through pull requests.
- Publishing and releases happen only from stable `main`.

See `DEVELOPMENT-WORKFLOW.md` for the exact folder roles and promotion flow.

For plugin behavior and implementation details, see:

- `./plugins/anyone-can-code/README.md`
- `./plugins/anyone-can-code/IMPLEMENTATION-SOURCE-OF-TRUTH.md`
- `./plugins/anyone-can-code/VALIDATION.md`

## License

MIT. See `LICENSE`.
