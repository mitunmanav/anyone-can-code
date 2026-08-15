# Anyone Can Code Memory Contract

This contract defines ACC memory and the first Markdown backend.

## Source Of Truth

- Durable memory is linked Markdown on disk.
- ACC works when no viewer is installed.
- Machine indexes are disposable caches rebuilt from Markdown.
- JSONL memory is migration input only. Current MCP writes durable notes as
  Markdown.
- Maintainer project notes and end-user memory are separate stores.

## Default Storage

Default project storage path:

```text
.codex/anyone-can-code/memory/notes/
```

Setup must display this path and allow user change before first durable memory
write. The selected path is recorded in:

```text
.codex/anyone-can-code/settings/preferences.json
```

Required memory folders:

```text
memory/
  raw/                 # sources only — AI never rewrites
  notes/               # durable wiki pages (Markdown notes)
    project/
    user/
    shared/
    lessons/
    failures/
    decisions/
    evidence/
    archive/
  wiki/
    index.md           # human catalog (rebuild from notes)
    log.md             # append-only change log
  index/               # machine cache (rebuildable JSON)
  imports/
```

`index/` is rebuildable JSON. `wiki/index.md` is the human catalog. `raw/` is
immutable source drops. `imports/` holds receipts and snapshots.

**Native Codex memories are never used.** ACC wiki is the only product memory.

## Two Drawers

Memory lives in two separate drawers that never mix:

- **Project drawer** — inside each project at
  `.codex/anyone-can-code/memory/`. Holds decisions, lessons, failures,
  evidence for THAT project only. Moves and deletes with the project.
- **User drawer** — one global folder at
  `~/.codex/anyone-can-code/user-memory/` (override:
  `ACC_USER_MEMORY_ROOT`). Holds taste only: style, common words, model
  likes. Kinds allowed: `preference`, `pattern`. Project facts are
  rejected with a plain-words error.

`$update` migrates old project-local user notes: taste moves to the user
drawer, project facts are re-scoped to the project drawer, with a receipt.

## MCP Backend

Bundled MCP tools keep stable names where possible:

- `store_feedback`: writes or reinforces one Markdown note; refreshes
  `wiki/index.md` and appends `wiki/log.md`.
- `retrieve_context`: reads Markdown notes and returns top 3-5 advisory items.
- `promote_memory`: increases trust for one note.
- `revoke_memory`: downgrades or revokes one note.
- `search_shared`: searches only shared notes.
- `rebuild_index`: rebuilds disposable `index/memory-index.json` and
  human `wiki/index.md`.
- `wiki_brief`: short index-first session brief (capped).
- `lint_wiki`: health check (empty wiki, orphan links, raw without notes).
- `ingest_raw`: copy a user-selected source into `raw/` with explicit consent.
- `import_session_files`: imports user-selected files into scoped Markdown notes
  and writes an import receipt.

## Viewer Modes

Supported setup choices:

- `none`: store linked Markdown and continue.
- `obsidian`: optional third-party viewer.
- `acc-viewer`: future work only, not available in this release.

Obsidian is optional third-party software. ACC must not bundle, redistribute,
modify, impersonate, silently install, silently launch, silently accept
agreements, or claim partnership with Obsidian.

## Consent Boundaries

ACC needs explicit consent before:

- downloading software or opening a download page;
- launching an app;
- opening or registering a vault;
- accepting any third-party agreement;
- migrating memory;
- moving files;
- overwriting files;
- importing existing local session files.

Declining a viewer must not block setup, learning, retrieval, migration, or
verification.

Windows setup maps explicit choices to `scripts/setup.py` flags. Viewer
selection alone performs no action. Download-page, install, and vault-open
actions require `--consent-viewer-action`. Session paths remain preview-only
unless `--confirm-import` is present.

Consented install uses Windows Package Manager package `Obsidian.Obsidian`.
ACC passes no package-agreement or source-agreement acceptance flags. Failed or
unavailable install does not block setup and falls back to
`https://obsidian.md/download`.

Vault opening is best effort. Receipt always includes visible manual fallback:
choose `Open folder as vault` in Obsidian and select chosen Markdown folder.

## Note Schema

Each memory note is Markdown with frontmatter:

```yaml
---
id: acc-memory-id
schema_version: 1
kind: project|user|shared|lesson|failure|decision|evidence|archive
scope: project|user|shared
status: active|superseded|revoked|archived
created_at: 2026-06-13T00:00:00Z
updated_at: 2026-06-13T00:00:00Z
source: manual|verified-work|user-correction|import
provenance: human-readable source summary
confidence: 0.0
reinforcement_count: 1
related: []
supersedes: []
---
```

Body sections:

```text
# Short title

## Summary

## Evidence

## Links

## Receipt
```

Links use normal Markdown links or wiki-style links when viewer supports them.
No viewer-specific link format may be required.

## Existing Session Import

Existing local session files are import sources only. ACC must not silently mine
them.

Import contract:

- user selects exact source path or folder;
- ACC shows scope before import: `project`, `user`, or `shared`;
- ACC snapshots or backs up source-readable inputs before changing output;
- ACC records provenance for every imported note;
- ACC deduplicates by stable hash and normalized summary;
- ACC writes receipt under `memory/imports/`;
- ACC labels imported notes with `source: import`;
- ACC allows dry-run before write;
- ACC does not delete source files.
- ACC snapshots every selected source before writing any Markdown note.
- ACC skips a normalized content hash already present in Markdown, so rerunning
  the same import is safe and resumable.
- ACC verifies written Markdown before marking the receipt `verified`.
- Any snapshot, write, index, or verification failure restores the pre-import
  Markdown tree, writes a rollback receipt, and leaves every source intact.

## Legacy JSONL Upgrade

`$update` migrates only known ACC-owned legacy memory files. It does not scan
arbitrary project folders or local Codex sessions.

Upgrade order:

1. refresh plugin source/runtime through Codex marketplace management;
2. run `$update` in the project;
3. `$update` backs up all supported ACC project data;
4. known legacy JSONL memory is copied to `memory/imports/backups/`;
5. deduplicated Markdown notes are written and verified;
6. legacy JSONL remains in place after success;
7. success or rollback receipt is written under `memory/imports/`.

User-selected session files use setup's explicit `--import-source`,
`--import-scope`, and `--confirm-import` path. `$update` never silently adds
session paths.

## Settings Contract

Required settings:

- `memory_path`
- `memory_mode`
- `viewer_mode`
- `import_sources`
- `import_scope`
- `production_repo_caution`
- `approval_mode` (`off` | `ask` | `allowlist` | `strict`) — ACC soft PermissionRequest layer only; not Codex host `/permissions`
- `approval_allowlist` (string list; used when `approval_mode` is `allowlist`)

Default values:

```json
{
  "memory_path": ".codex/anyone-can-code/memory/notes",
  "memory_mode": "portable-markdown",
  "viewer_mode": "none",
  "import_sources": [],
  "import_scope": "ask",
  "production_repo_caution": true,
  "approval_mode": "ask",
  "approval_allowlist": []
}
```

Each setup run writes unique Markdown and JSON receipts under:

```text
.codex/anyone-can-code/state/receipts/
```

Receipt records storage, viewer choice/action/result, import paths/scope/result,
and confirms no hidden registry change, file move/delete, or third-party
agreement acceptance occurred.

Production-repo caution means ACC asks before broad imports, migrations, moves,
or overwrites in a project that looks like real production work.
