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
3. Build derived capability registry with provider, manifest source, health,
   last probe, and ACC fallback. Registry is not durable workflow truth.
4. Probe matched capability before important use.
5. Skip malformed manifests, missing skill folders, weak matches, unhealthy
   capabilities, and ACC itself.
6. Build a bounded specialist assignment through
   `scripts/front_door.py`. ACC remains workflow owner.
7. Assignment names exact request, allowed output, permissions, forbidden
   workflow controls, and return path.
8. Report: `Found [plugin-name] for [capability]. Using bounded specialist help.`
9. Block foreign plans, trackers, approval gates, commit rules, response-style
   changes, and workflow-owner changes.
10. Keep usable technical output, return it to ACC, verify it, then continue.
11. If plugin is unavailable, unhealthy, fails, or returns no usable result, report
   fallback and continue with ACC.

## When to use

Automatically at the start of any build pipeline to prevent duplication.
Also when the user mentions using another tool that might have plugin coverage.

## When NOT to use

Cache scanning is approximate. Not all installed features may be detectable.
Never say a plugin is available unless its installed manifest was read.
If routing fails or produces no usable result, fall through to local ACC work.
Workflow handoff is allowed only when user explicitly requests that exact
plugin to become workflow owner.
