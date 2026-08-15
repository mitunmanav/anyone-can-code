# PROOF — dr-memory-hygiene

**Branch:** `feature/dr-memory-hygiene`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**No push. No merge.**

## What

ACC **wiki** memory hygiene (not Codex `/memories`):

| Piece | Path |
|-------|------|
| Helper | `plugins/anyone-can-code/scripts/memory_hygiene.py` |
| Skill | `plugins/anyone-can-code/skills/memory-hygiene/SKILL.md` |
| UI | `skills/memory-hygiene/agents/openai.yaml` → **ACC memory hygiene** |
| Policy | `allow_implicit_invocation: false` (explicit only) |
| Tests | `plugins/anyone-can-code/tests/test_memory_hygiene.py` |

## Behavior

1. **Age notes** — mtime ≥ **28 days** (Copilot Memory unused retention) → stale list.
2. **Flag secrets** — api_key/token/password, `sk-…`, bearer, `gh*_` PAT; report scrubbed preview only.
3. **Never store full chat** — `validate_store_candidate` rejects multi-turn transcripts / bulk dumps.
4. **Scan is read-only** — no write until user YES (skill path).
5. **Product path** — `.codex/anyone-can-code/memory/notes/` only. Never `~/.codex/memories/`.

## Docs grounding (WEB + Codex)

### WEB — GitHub Copilot Memory

Source: https://docs.github.com/en/copilot/concepts/agents/copilot-memory

- Unused stored fact/preference **deleted after 28 days** (timer may reset on successful validate/use).
- Repo-level facts stored **with citations** to supporting code; JIT verify before use.
- Changelog / VS Code agent memory: same **28-day** auto-expire.

ACC maps 28-day unused age → **stale flag** (suggest archive/refresh; not silent delete).

### Codex — Memories + redaction

Via `python3 "codex docs/read-docs.py" --show codex/memories`:

- Local Codex memories store under `~/.codex/memories/`; **off by default** (`[features] memories = true` to enable).
- **“Codex redacts secrets from generated memory fields”** — still: don’t store secrets; review before share.
- ACC product memory stays **wiki Markdown** + `native_memory_policy.py` keeps native memories **off**.
- Skill/docs honesty: dual-memory confusion risk → this skill names ACC wiki only.

Also noted: Chronicle (separate desktop preview) stores unencrypted memory files under extensions path — **out of scope**; ACC does not write there.

## Checks run

```bash
python3 -m pytest \
  plugins/anyone-can-code/tests/test_memory_hygiene.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_ship_set.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py \
  -q
```

CLI:

```bash
python3 plugins/anyone-can-code/scripts/memory_hygiene.py --help
python3 plugins/anyone-can-code/scripts/memory_hygiene.py --project-root . --json
```

## Manual (user)

1. `$memory-hygiene` in Codex.
2. Confirm report (stale / secret / full-chat).
3. Say no → nothing written. Say yes → only chosen scrub/archive/short rewrite.

## Not in this lane

- No push / merge
- No auto-fire every turn
- Does not replace `$wiki` doctor or hook auto-memory
- Does not enable Codex native memories
