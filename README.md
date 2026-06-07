# Anyone Can Code Marketplace

This repository contains the **Anyone Can Code** Codex plugin marketplace and plugin source.

## Repository layout

- `/.agents/plugins/marketplace.json` - marketplace definition
- `/plugins/anyone-can-code` - plugin source bundle

## Releasing

Releases are automated with GitHub Actions.

1. Update plugin version in `/plugins/anyone-can-code/.codex-plugin/plugin.json`.
2. Commit and push the change.
3. Create and push a version tag in the format `vX.Y.Z` (must match plugin.json version).
4. GitHub Actions will:
   - validate tag/version match,
   - package `plugins/anyone-can-code` as a zip,
   - publish/update a GitHub Release with the zip and SHA256 checksum.

## Development

For plugin behavior and implementation details, see:

- `/plugins/anyone-can-code/README.md`
- `/plugins/anyone-can-code/IMPLEMENTATION-SOURCE-OF-TRUTH.md`
