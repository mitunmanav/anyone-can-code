---
name: bridge
description: "Installed plugin detection. Reads installed manifests, routes confident capability matches, and falls back to ACC when coverage is missing or unusable."
---

# Bridge

Detect and route to other installed plugins.

## How it works

1. Use `scripts/front_door.py` to scan
   `~/.codex/plugins/cache/*/*/*/.codex-plugin/plugin.json`.
2. Read structured manifest name, descriptions, declared skills path, and skill
   frontmatter descriptions.
3. Skip malformed manifests, missing skill folders, weak matches, and ACC
   itself.
4. Treat the best confident match as advice. Do not execute plugin code during
   discovery.
5. Report: `Found [plugin-name] for [capability]. Routing there.`
6. If the plugin is unavailable, fails, or returns no usable result, report the
   fallback and continue with ACC.

## When to use

Automatically at the start of any build pipeline to prevent duplication.
Also when the user mentions using another tool that might have plugin coverage.

## When NOT to use

Cache scanning is approximate. Not all installed features may be detectable.
Never say a plugin is available unless its installed manifest was read.
If routing fails or produces no usable result, fall through to local ACC work.
