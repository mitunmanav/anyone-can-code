---
name: bridge
description: "Installed plugin detection. Scans ~/.codex/plugins/cache/ for installed plugins. If an installed plugin already handles a requested task, routes to it. Never rebuilds what another plugin provides. Cache scan is advisory — best-effort detection of installed plugin coverage."
---

# Bridge

Detect and route to other installed plugins.

## How it works

1. Scan `~/.codex/plugins/cache/` for installed plugin manifests
2. For each detected plugin: read its plugin.json to understand what skills it provides
3. If the current task matches another plugin's capability: route the task there
4. Report: "Found [plugin-name] which handles [capability]. Routing there."

## When to use

Automatically at the start of any build pipeline to prevent duplication.
Also when the user mentions using another tool that might have plugin coverage.

## When NOT to use

Cache scan is filesystem inspection — it's approximate. Not all installed features may be detectable.
If routing fails or produces wrong results, fall through to local build.
