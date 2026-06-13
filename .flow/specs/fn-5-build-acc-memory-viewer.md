# Build ACC-owned memory viewer

## Goal & Context

Provide an optional ACC-owned interface for browsing portable Markdown memory. This is future work. It must not block Markdown storage, learning, retrieval, or optional Obsidian use.

## Scope

- Start with list, search, filters, provenance, confidence, archive, edit, and delete controls.
- Add graph view only after usage proves it useful.
- Use a proven graph library rather than building graph layout from scratch.
- Read the same Markdown source of truth used by all other viewers.

## Boundaries

- Do not start during the portable Markdown memory migration.
- Do not create a second memory database.
- Do not make viewer installation mandatory.
- Do not copy full Obsidian behavior.

## Acceptance Criteria

- Viewer is optional.
- Markdown remains source of truth.
- Core ACC works when viewer is absent.
- First release prioritizes search and memory controls over graph decoration.
- Graph support has separate evidence proving usefulness, performance, and accessibility.
