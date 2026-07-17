# ACC Offline Auto-Memory — Architecture (research record)

Date: 2026-07-17 · Author: Mitun · Status: design locked, plan at
`docs/superpowers/plans/2026-07-17-offline-auto-memory.md`

Grounded in scraped Codex docs (`codex docs/read-docs.py --show codex/hooks`,
`--show plugins/build`). Never invent Codex APIs.

## One-line law

Memory is a side-effect of Codex hooks, not a skill anyone remembers to run.
NOW (live state) alone must be enough to resume.

## Codex facts that bound the design (from docs, verified)

- Hooks: `SessionStart` (matcher `startup|resume|clear|compact`),
  `UserPromptSubmit` (gets `prompt`), `Stop` (gets `last_assistant_message`,
  `stop_hook_active`), `PreCompact`/`PostCompact` (matcher `manual|auto`),
  `PreToolUse`/`PostToolUse`/`PermissionRequest` (matcher tool name),
  `SubagentStart`/`SubagentStop`.
- `Stop` and `SubagentStop` **must emit JSON on stdout** when exiting 0.
  Plain text is invalid for those events.
- `PreCompact`/`PostCompact`/`PostToolUse` plain stdout is **ignored**.
  Only `SessionStart` + `UserPromptSubmit` accept plain-text context.
- SessionStart JSON: `hookSpecificOutput.additionalContext` → developer context.
- Multiple matching hooks run **concurrently** → disk writes need a lock.
- Hook `timeout` default is 600 s → memory hooks must set small timeouts.
- Plugin hooks are skipped until the user reviews + trusts them (`/hooks`).
  Trust is recorded against the hook hash → every plugin update re-requires trust.
- Env for plugin hooks: `PLUGIN_ROOT`, `PLUGIN_DATA` (+ CLAUDE_* aliases).
- Native Codex `/memories`: delayed, LLM-based, skips near rate limit —
  banned as product memory (ACC `native_memory_policy.py` already enforces).

## Architecture

One stdlib library, no daemon, no second process. Hooks, MCP, doctor all call
the same functions in-process.

```
Codex event ──stdin JSON──▶ hook script (existing hooks/hooks.json wiring)
                                │
                        memory_core / memory_promote / memory_index
                                │
        ┌───────────────────────┼──────────────────────────┐
        ▼                       ▼                          ▼
  BOSS (live)             TRUTH (append)              INDEX (cache)
  canonical state         events: signal log,         memory.sqlite FTS5
  (+ turn_status,         prompt log, turn ledger     WAL; delete=rebuild
  open_ask,               (fsync per line)            LIKE fallback if
  last_decision)          notes/*.md (atomic,         FTS5 missing
  + NOW.md mirror         frontmatter, dedup)
        └───────────────────────┴──────────────────────────┘
                                │
              SessionStart inject: NOW block + crash flag + top lessons
              MCP search / $status / $fix = backup + repair only
```

Key decision vs earlier drafts: **no new `now.json`.** ACC already has a
transactional canonical state (`canonical_state.update_canonical_state`,
rollback + bounded retry). A parallel live file = two truths = the disease.
Boss = canonical state, extended with three fields. `NOW.md` is a
human-readable mirror, written atomically, never read back by code.

## Three drawers

| Drawer | Store | Injected? |
|---|---|---|
| Live | canonical state + NOW.md mirror | Always, first, ≤ ~700 chars |
| Truth | signal/prompt/turn jsonl + notes/*.md | Never wholesale |
| Index | memory.sqlite (FTS5) | No — feeds top 3 lessons only |

## Hook → write map

| Event | Writes |
|---|---|
| UserPromptSubmit | prompt log line (fsync); `turn_status=open`, `open_ask`; promote want/correction notes (rules, ≤3/turn) |
| Stop | ALWAYS state rewrite (`turn_status=closed`, next, `last_decision`); turn-ledger line; promote decision notes; NOW.md mirror; **no proposals** |
| PreCompact | capsule (existing, kept) |
| PostCompact | short Goal/Next systemMessage (existing, kept) |
| SessionStart | heartbeat.json write; inject NOW block + crash-resume flag + lessons |
| PostToolUse | failure signal only (existing guard path) |

## The open-turn flag (crash resume)

UserPromptSubmit marks the turn open with the ask. Stop marks it closed.
Died before Stop (kill / crash / limit) → next SessionStart sees
`turn_status=open` and injects: `CRASH RESUME: last request may be
unfinished: <ask>`. Converts the worst failure (death before Stop) from
silent loss to an explicit resume line. Cost: two state fields.

## Auto-capture (no AI)

Promote rules (regex, scrubbed text): want / decision / correction (+ failure
via existing verified_failure signals). Negative guard (`never mind`, …).
Dedup: sha256 of normalized excerpt → registry; duplicate bumps
`reinforcement_count` instead of a new note. Note format = the exact
frontmatter the existing `recall_memory_notes` parser reads
(`kind`, `status`, `reinforcement_count`, `## Summary`) — recall needs only
a kind-set widening. Caps: ≤3 notes/turn, excerpt ≤200 chars, prompt log
line ≤4k, stop summary ≤2k (existing).

Rank: `bm25 × kind_weight × 1/(1+age_days/30) × (1+ln(1+reinforcement))`.
Weights: correction 3.0 · want 2.5 · decision 2.5 · mistake/lesson 2.0 ·
failure 1.5 · other 1.0.

## Durability

- jsonl appends: `flush()` + `os.fsync()` per line.
- jsonl rotation: write tmp → `os.replace` (the old in-place rewrite could
  lose the whole ledger on a kill mid-rotate — fixed).
- All non-append files: tmp → fsync → `os.replace` (atomic on NTFS,
  same volume).
- Readers tolerate one torn tail line (skip unparseable).
- SQLite: WAL, `synchronous=NORMAL`; pure cache; corrupt = delete + rebuild
  from notes.
- Lock: `O_CREAT|O_EXCL` lockfile, 2 s wait, steal stale >10 s (hooks run
  concurrently per docs).
- Kill-test harness in the gate: subprocess writer SIGKILLed at random
  offsets; after every kill state parses, ledgers lose ≤ the torn tail,
  index rebuilds.
- Write order: journal line first, state rename second — the fsynced journal
  bounds any rename loss.

## Scale

Inject is constant-size (memory block ≤1500 chars) no matter how big the
store grows. Journal rotates (existing 500/200-line rotation, now safe).
Notes uncapped — FTS5 handles 100k+ rows; recall switches from rglob scan to
index when notes > 50. Memory indexes conversation artifacts, never source
code, so codebase size is irrelevant.

## Hardware tiers

Detect via stdlib (`GlobalMemoryStatusEx` on Windows, `/proc/meminfo` else,
`os.cpu_count`). weak (<8 GB) = FTS5 only · mid (8–16 GB) = + lazy small
ONNX embed (bge-small-en-v1.5 ~130 MB / MiniLM-L6 ~80 MB) · strong (≥16 GB)
= + sqlite-vec + RRF. Embeddings are **out of v1**: separate plan, only
after the kill-test gate and a live Windows resume proof are green.
Embeds never sit on the write path and are never required for resume.
Doctor reports the real backend — no fake labels.

## Hook trust (the real killer)

If hooks are untrusted, none of this runs — and every plugin update changes
hook hashes, re-requiring trust. Fixes: (1) SessionStart writes
`heartbeat.json`; (2) `memory_doctor.py` + MCP status + `$setup` check
heartbeat age from **non-hook paths** and print the exact fix
("run /hooks, trust anyone-can-code, restart"); (3) install + update copy
makes trust step 1 with a one-sentence why. No bypass flags.

## Reuse / replace / kill (grok worktree)

| Piece | Verdict |
|---|---|
| hooks/hooks.json full wiring (all 10 events, PowerShell launcher) | Reuse |
| canonical state transaction (`write_state`) | Reuse as boss |
| MCP note format, merge/dedup, redaction, disposable index tests | Reuse pattern |
| `load_session.build_context`, capsule, guard signals | Reuse + extend |
| `state.append_jsonl` | Fix (fsync + safe rotate) |
| `save_session.wiki_stop_proposals`, `wiki_memory.propose_saves` / `stop_save_prompt` | **Kill** — write or discard, never "please save" |
| `store_feedback`/`retrieve_context` MCP as product write path | Demote to backup/debug |
| Skill copy teaching "$wiki to remember" | Kill wording; skills = repair verbs |
| `native_memory_policy.py` | Keep |

## Risks — resolved vs residual

| Risk | Resolution |
|---|---|
| Windows fsync (no dir fsync) | Journal-first write order + fsynced appends bound loss to one rename; kill-test proves; residual power-cut window documented, accepted |
| Hook trust decay on update | Heartbeat + non-hook detection + exact fix copy + update-flow re-trust step (plan tasks, not hopes) |
| Regex promote quality | Fixture corpus test (positives AND negatives); rules in one data table; journal is the safety net for misses |
| Weak `last_assistant_message` | User prompt is the trusted signal; open-turn flag covers the gap; optional structured trailer is bonus only |
| Concurrent hook races | Lockfile + concurrency kill-test in P0 gate |
| sqlite-vec / onnx packaging on Windows | Deferred entirely to a post-v1 plan behind the proof gate; product complete without it |
| PreToolUse shell coverage gaps (`unified_exec`) | Failure capture is a bonus signal; accepted |

## Avoid list (unchanged)

agentmemory as product · ruflo · ChromaDB · native /memories as brain ·
PreCompact stdout inject · LLM-required extraction · full-transcript vector
dumping · any second memory plugin ecosystem.
