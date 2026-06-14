# fn-7-build-isolated-session-analyzer Build isolated session analyzer

## Goal & Context
<!-- scope: business -->

Create a manually invoked local session-analysis tool for Codex `.md` exports placed in one fixed Desktop inbox. Tool lives beside ACC, never inside it, and records each run in a separate Obsidian dump area for later human-reviewed promotion into ACC brain.

## Architecture & Data Models
<!-- scope: technical -->

Tool root: `C:\Users\Mitun Manav G Y\Desktop\Plugin development\session-analyzer`.

Fixed inbox: `C:\Users\Mitun Manav G Y\Desktop\SESSION ANALYSER MD FILES`.

Runtime enumerates direct `.md` files from only that inbox. It never recurses or accepts caller-supplied input paths. It performs read-only parsing and writes a new timestamped run directory only beneath `I:\Obsidian vaults\Projects\ACC Session Analyzer Dump`. Each run contains manifest/checksums, exact mechanical facts, sanitized evidence, and a saved deep-analysis prompt. Chat performs interpretation later. No automatic promotion into `Projects\Anyone Can Code`.

Hard path guards reject ACC repo, `.flow`, `.codex`, hooks, configs, worktrees, Git metadata, analyzer source, and any output path outside the dump root.

## API Contracts
<!-- scope: technical -->

Manual command accepts only an optional run label. It reads all direct `.md` files in the fixed inbox, ignores subfolders and non-Markdown files, and searches nowhere else. Success creates one immutable run folder. Missing/empty inbox or parse/runtime failure returns non-zero without a promoted brain note.

## Edge Cases & Constraints
<!-- scope: technical -->

- Inputs remain unchanged.
- Existing dump runs are never overwritten.
- Symlinks/reparse points and resolved paths must pass boundary checks.
- Raw secret-shaped values are not copied into sanitized output.
- Tool has no hooks, automation, background process, MCP server, plugin manifest, Git operation, or ACC dependency.
- Network access is not required.

## Acceptance Criteria
<!-- scope: both -->

- **R1:** Tool exists only in sibling `session-analyzer`, outside ACC repo.
- **R2:** Run occurs only from explicit command and reads only direct `.md` files from the fixed inbox.
- **R3:** Runtime cannot write outside Obsidian dump root or into ACC brain.
- **R4:** Runtime cannot read protected Plugin development system paths or search outside the fixed inbox.
- **R5:** Valid session files produce checksummed manifest, exact facts, sanitized evidence, and saved analysis prompt.
- **R6:** Tests prove fixed-inbox filtering, protected paths, overwrite attempts, malformed records, empty/missing inbox, and normal runs behave safely.
- **R7:** Obsidian records architecture, run lifecycle, fixed inbox, and manual approval gate for promoting findings into ACC brain.
- **R8:** No GitHub action occurs.

## Boundaries
<!-- scope: business -->

No ACC plugin packaging or source changes. No automatic run. No recursive session discovery. No caller-selected input paths. No automatic Obsidian brain promotion. No background monitoring. No remote upload. No direct analysis until user explicitly commands a run.

## Decision Context
<!-- scope: both -->

Fixed inbox chosen to avoid searching, accidental file selection, and wasted work. Two-stage dump flow chosen over direct brain writes. Dump keeps complete audit artifacts separate; user and chat review useful findings before copying concise conclusions into trusted ACC brain. This reduces secret leakage, bad parsing, and memory contamination while preserving evidence.
