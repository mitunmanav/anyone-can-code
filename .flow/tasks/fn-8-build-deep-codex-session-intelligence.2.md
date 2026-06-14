---
satisfies: [R1, R2, R4, R5, R7, R10, R11, R16]
---

## Description
Replace generic recursive analysis with a one-pass event-aware normalizer that emits versioned session, turn, message, prompt-layer, tool, token, timing, and compaction records while preserving unknown fields and provenance.

**Size:** M
**Files:** `../session-analyzer/session_analyzer.py`, `../session-analyzer/session_records.py`, `../session-analyzer/tests/test_session_records.py`

## Approach
- Keep existing fixed inbox, path rejection, immutable run directory, hashing, and cleanup patterns.
- Stream JSONL once per source.
- Use explicit adapters keyed by outer record type and payload subtype.
- Build bounded indexes for session, turn, and call IDs; never retain unnecessary raw content.
- Record unknown records and paths instead of silently ignoring them.

## Investigation targets
**Required:**
- `../session-analyzer/session_analyzer.py:16-147` - boundaries to preserve.
- `../session-analyzer/session_analyzer.py:149-281` - sanitizer and analyzer core.
- `../session-analyzer/docs/event-schema.md` - task .1 contract.
- `../session-analyzer/tests/test_session_analyzer.py` - regression suite.

**Optional:**
- `offical-codex-docs/core/hooks.md` - event field concepts.
- `offical-codex-docs/cli/reference.md` - JSONL/app-server terminology.

## Acceptance
- [ ] One normalized event stream feeds both exhaustive forensic records and compact downstream metrics without rereading source files.
- [ ] Every normalized item receives stable evidence identity suitable for drill-down links.
- [ ] Every parsed source record is classified, normalized, or retained as unknown with source/line provenance.
- [ ] Schema inventory and normalized sessions/turns/tools outputs are versioned.
- [ ] Parsing remains streaming and reads only fixed direct `.md` files.
- [ ] Existing source immutability, protected-tree, dump-root, symlink, malformed-line, and overwrite tests remain green.
- [ ] Prompt and sensitive content is not copied into aggregate output before privacy filtering.

## Done summary
TBD

## Evidence
- Commits:
- Tests:
- PRs:
