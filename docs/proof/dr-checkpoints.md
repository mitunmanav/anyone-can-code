# Proof: feature/dr-checkpoints

**Branch:** `feature/dr-checkpoints`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** ACC-shaped file checkpoints (pattern only — not Cline clone)  
**Push/merge:** none  
**Hooks:** still **10** (no hooks.json change)

## Docs first

### Web (Cline / shadow-git pattern)

| URL | What we took |
| --- | --- |
| https://docs.cline.bot/core-workflows/checkpoints | Shadow git separate from project git; restore files / task / both; compare; auto after tool use |
| https://memo.d.foundation/breakdown/cline | ShadowGitManager sketch (`refs/cline/shadow`, checkpoint commits) |
| https://medium.com/codex/clines-backroom-git-the-secret-history-of-view-changes-8523c7c6437f | Checkpoints = commits in hidden repo under editor storage; not user `.git` |
| https://medium.com/codex/cline-x-ray-turning-clines-shadow-git-into-an-inspectable-evidence-layer-04a5815ed539 | Diffs against checkpoint commits, not working tree alone |
| https://github.com/cline/cline/issues/8273 | Risk of shadow-git fighting real `.git` (ACC avoids real shadow git) |
| https://github.com/cline/cline/issues/9590 | Large monorepo corruption reports from full shadow-git approach |
| https://code.claude.com/docs/en/checkpointing | Claude Code rewind: restore code / conversation / both |
| https://code.visualstudio.com/docs/chat/chat-checkpoints | VS Code chat checkpoints restore workspace to prior state |
| https://kiro.dev/docs/cli/experimental/checkpointing | Shadow bare git outside project (same idea family) |

### Codex topics read

| Topic | Use for this feature |
| --- | --- |
| **Hooks** (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, `PreCompact`, `PostCompact`, …) | Confirm ACC keeps **10** hook events; checkpoints are **skill + script**, not a new hook |
| **Skills** (`SKILL.md` frontmatter + optional `agents/openai.yaml`) | `$checkpoint` packaging; `display_name`; `allow_implicit_invocation: false` |
| Plugin hooks load | Hooks stay trusted for memory; checkpoint restore stays explicit user action |

References used in research:

- https://learn.chatgpt.com/docs/hooks — event table + PreToolUse shape
- Skill layout mirror: sibling DR skills (`parallel-fix`, `ledger`)

## Design choice (ACC, not clone)

| Cline-style | ACC this branch |
| --- | --- |
| Shadow git repo + commits after tool use | Explicit `$checkpoint` save only |
| core.worktree → workspace | Blobs under `.codex/anyone-can-code/state/checkpoints/` |
| Restore files / task / both | Restore **files** only (conversation is Codex’s) |
| Risk of `.git` rename / monorepo pain | Never touch project `.git` |

## Delivered

| Item | Path |
| --- | --- |
| Script | `plugins/anyone-can-code/scripts/checkpoints.py` |
| Skill | `plugins/anyone-can-code/skills/checkpoint/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/checkpoint/agents/openai.yaml` |
| Tests | `plugins/anyone-can-code/tests/test_checkpoints.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC checkpoint"` |
| Explicit-only | `tests/test_skill_discovery.py` → `checkpoint` in `EXPLICIT_ONLY` |
| Proof | `docs/proof/dr-checkpoints.md` |

## Behavior

1. **save** — walk project (ignore `.git`, `node_modules`, `.codex`, venvs, caches) → `meta.json` + `files.json` (path/sha256/size) + `blobs/<sha256>`
2. **list** — newest first (`index.json` + folder scan fallback)
3. **restore** `<id>` — write stored blobs back; skip missing blobs / never rewrite `.git`; does **not** delete files added after the snapshot
4. Caps: max file blob 1.5MB; total blob budget 40MB; max 5000 files

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_checkpoints.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py -q
# 14 passed

python3 -c "import json; print(len(json.load(open('plugins/anyone-can-code/hooks/hooks.json'))['hooks']))"
# 10
```

Skill budget: `SKILL.md` ≈ **2074** chars (limit 4000).

Live demo (tmp project): save → mutate → restore rewound `src/app.py`.

## How to re-check

```bash
rm -rf /tmp/acc-cp-demo && mkdir -p /tmp/acc-cp-demo/src
echo "print(1)" > /tmp/acc-cp-demo/src/app.py
python3 plugins/anyone-can-code/scripts/checkpoints.py --project /tmp/acc-cp-demo save --label demo --json
python3 plugins/anyone-can-code/scripts/checkpoints.py --project /tmp/acc-cp-demo list
# mutate, then:
python3 plugins/anyone-can-code/scripts/checkpoints.py --project /tmp/acc-cp-demo restore <id> --json
```

## PASS/FAIL

**PASS** — save/list/restore + skill registration + path contract green.  
**Hooks count:** 10 unchanged.  
No push. No merge.
