# Anyone Can Code Marketplace

This repository contains the **Anyone Can Code** Codex plugin marketplace and plugin source.

## About this project

This project is built for a **non-technical builder** who wants to create a highly efficient Codex desktop plugin experience.

Core product goals:

- Near-zero learning curve for first-time users
- Self-learning plugin behavior through memory and workflow feedback
- Clear, guided flow from idea to verified result

## Repository layout

- `/.agents/plugins/marketplace.json` - marketplace definition
- `/plugins/anyone-can-code` - plugin source bundle

## Downloads

These badges track this repository (`mitunmanav/anyone-can-code`). If you fork or rename it, replace the `owner/repo` segment in both badge URLs.

![Total Downloads](https://img.shields.io/github/downloads/mitunmanav/anyone-can-code/total?style=for-the-badge&label=Total%20Downloads)
![Latest Release Downloads](https://img.shields.io/github/downloads/mitunmanav/anyone-can-code/latest/total?style=for-the-badge&label=Latest%20Release%20Downloads)

## Releasing

Releases are automated with GitHub Actions.

1. Update plugin version in `./plugins/anyone-can-code/.codex-plugin/plugin.json`.
2. Commit and push the change.
3. Create and push a version tag in the format `vX.Y.Z` (must match plugin.json version).
4. GitHub Actions will:
   - validate tag/version match,
   - package `plugins/anyone-can-code` as a zip,
   - publish/update a GitHub Release with the zip and SHA256 checksum.

## Development

For plugin behavior and implementation details, see:

- `./plugins/anyone-can-code/README.md`
- `./plugins/anyone-can-code/IMPLEMENTATION-SOURCE-OF-TRUTH.md`
