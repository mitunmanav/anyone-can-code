# MERGE_SYNC_REPORT — main → grok

**Date:** 2026-07-16  
**Branch:** `grok` only (inside `.worktrees/grok`)  
**Action:** `git merge main` into grok. Main was **not** checked out, committed, or pushed.  
**Next gate:** Fable re-checks this report → Mitun does final grok→main (not done here).

---

## 1. Which 8 main commits came in

These were on `main` and not yet on `grok` (merge base `0af821c`):

| Commit | Subject |
|--------|---------|
| `8fa3a9c` | docs: add multi-language README set for global readers |
| `a3abf1d` | docs: add public roadmap (beta.4 building, beta.5 direction) |
| `9ce4875` | docs: move non-English READMEs into i18n/ |
| `c09c065` | docs: rename i18n/ to readmes/ |
| `206f14c` | docs: point language links at readmes/ |
| `08bca51` | docs: remove broken star-history chart |
| `2ca27b8` | docs: surface public roadmap on README |
| `de9422b` | chore: harden gitignore for private dev files; use python3 in AGENTS |

Also pulled via auto-merge (same commit set): `ROADMAP.md`, `readmes/*`, `AGENTS.md` (`python` → `python3`).

---

## 2. `.gitignore` — private-file rules kept

### Conflict status

**No conflict markers.** Git auto-merged `.gitignore` to main’s hardened file, which is a **superset** of grok’s prior rules (grok’s `.worktrees/`, `.run-logs/`, `.runtime/`, `__pycache__` already present on main’s version).

### Final private-file / never-public rules (paste)

```gitignore
# === runtime / local agent state — never public ===
/.codex/
/plugins/anyone-can-code/.codex/*
!/plugins/anyone-can-code/.codex/agents
/plugins/anyone-can-code/.opencode/
/.claude/
/.claude-flow/
/.tokensave/
/.codegraph/
/data/
/skills-lock.json
.worktrees/
.run-logs/
.runtime/
.pytest_cache/
**/__pycache__/
*.pyc
*.bak-*
CLAUDE.md
CLAUDE.md.bak*
CLAUDE.local.md
AGENTS.local.md

# === private sessions / exports / audits — never public ===
/codex sessions/
/codex testing sessions/
/codex docs/
/2026-*-local-command-*.txt
/2026-*-conversation-exported-*.txt
/**/*session*export*
/**/*AUDIT*
!plugins/**/tests/**

# === internal development rules & process — never public ===
/docs/plans/
/docs/superpowers/
/docs/SESSION_HANDOFF_*.md
/docs/ACC_TRIAL_*.md
/docs/CLAUDE_HARNESS_DESIGN.md
/docs/ACC_LOOP_PROMPT.md
/docs/ACC_IMPROVEMENT_LOOP.md
/docs/ACC_PLUGIN_GOALS.md
/docs/ACC_PLUGIN_BUILD_RULEBOOK.md
/docs/ACC-OPERATING-CONTRACT.md
/docs/**/*RULEBOOK*
/docs/**/*OPERATING*
/docs/**/*HARNESS*
/docs/**/*LOOP*
*.local.md
/scratch/
/tmp/
/.now/
/NOW.md
```

### Required main-side guards — all present

| Required rule | In final `.gitignore`? |
|---------------|------------------------|
| `CLAUDE.md` (main; broader than `/CLAUDE.md`) | yes L19 |
| `CLAUDE.md.bak*` | yes L20 |
| `CLAUDE.local.md` | yes L21 |
| `AGENTS.local.md` | yes L22 |
| `/codex sessions/` | yes L25 |
| `/codex testing sessions/` | yes L26 |
| `/codex docs/` | yes L27 |
| `/2026-*-local-command-*.txt` | yes L28 |
| `/2026-*-conversation-exported-*.txt` | yes L29 |
| `/**/*session*export*` | yes L30 |
| `/**/*AUDIT*` | yes L31 |
| `!plugins/**/tests/**` | yes L32 |
| grok extras: `.worktrees/`, `.run-logs/`, `.runtime/`, `**/__pycache__/` | yes L12–L16 |

Note: main uses bare `CLAUDE.md` (any path), not only `/CLAUDE.md`. That is **stricter** (hides more), not weaker.

### `git check-ignore` proof

```text
$ git check-ignore -v CLAUDE.local.md AGENTS.local.md CLAUDE.md
.gitignore:49:*.local.md	CLAUDE.local.md
.gitignore:49:*.local.md	AGENTS.local.md
.gitignore:19:CLAUDE.md	CLAUDE.md

$ git check-ignore -v "codex testing sessions/" "codex docs/" ".worktrees/"
.gitignore:26:/codex testing sessions/	codex testing sessions/
.gitignore:27:/codex docs/	codex docs/
.gitignore:12:.worktrees/	.worktrees/
```

Directory patterns end with `/`, so check-ignore needs a trailing `/` on those path args (git only treats them as dirs that way). Rules match.

### `git status --short` private leak check

None of the private paths appear as staged/tracked. Status after merge resolve only shows intentional merge paths + untracked `docs/CODEX_RESEARCH_PLAN.md` / `docs/FABLE_REVIEW.md` (not private session/export/audit files).

---

## 3. README.md conflict — what was combined

**Only content conflict:** top tagline / language links block.

| Side | Kept |
|------|------|
| **main** | Language links → `readmes/README.*.md`; roadmap badge + `ROADMAP.md` section (already auto-merged rest of file); multi-lang set on disk |
| **grok** | Dual-package table (Desktop + CLI); “Plain English → plan → build → check”; free plugins wording |

**Resolved header (union):**

1. Languages line (main)  
2. Tagline: plain-English flow (grok) + free Desktop+CLI plugins (grok expanded) + “plan, build, and check” sentence (main)

No side deleted. Rest of README (install both packages, roadmap table, links) already merged cleanly from main’s roadmap work + grok’s dual-package layout.

---

## 4. Any other conflicts

| Path | Status | Resolution |
|------|--------|------------|
| `.gitignore` | clean auto-merge | Kept main’s hardened union (superset) |
| `AGENTS.md` | clean auto-merge | `python` → `python3` from main |
| `ROADMAP.md` | added from main | kept |
| `readmes/*` | added from main | kept (8 languages) |
| `README.md` | **content conflict** | union as above |

No safety line, private-file guard, or public doc link was dropped to “win” the merge.

---

## 5. Test + doctor results

| Check | Result |
|-------|--------|
| `python3 -m pytest plugins/anyone-can-code/tests -q` | **507 passed**, 3 skipped, 67 subtests passed |
| `python3 -m pytest plugins/anyone-can-code-cli/tests -q` | **510 passed**, 3 skipped, 97 subtests passed |
| `python3 plugins/anyone-can-code/scripts/doctor.py --json` | **fail: 0**, pass: 27, warn: 11 (runtime install cache missing — normal on this worktree) |

Merge did not break tests. No code fixes required beyond README conflict resolve.

---

## 6. Confirm: grok now contains all of main

After this merge commit on `grok`:

- Every commit that was on `main` is an ancestor of `grok`.
- `grok` still has its own Fable-fix / wiring history on top.
- **Next `main` ← `grok` should be a clean fast-forward** (or equivalent no-conflict merge), with private-file gitignore already aligned.

**Not done here (by design):**

- No merge to `main`
- No push
- No checkout of `main`
- No force / reset / rebase / clean

---

## 7. Author / lock

- Author: Mitun only (no co-author / agent footer).  
- Worktree: `.worktrees/grok` branch `grok` only.  
- Fable re-checks this report → Mitun is the only final merge gate.
