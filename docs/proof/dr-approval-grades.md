# PROOF — dr-approval-grades

**Branch:** `feature/dr-approval-grades`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**No push. No merge.**

## What

ACC prefs **approval grades**: `off` | `ask` | `allowlist` | `strict`.

| Piece | Path |
|-------|------|
| Skill | `plugins/anyone-can-code/skills/approval-mode/SKILL.md` |
| UI label | `skills/approval-mode/agents/openai.yaml` → **ACC approval mode** |
| Policy | `allow_implicit_invocation: false` (explicit-only) |
| Helper | `plugins/anyone-can-code/scripts/approval_grades.py` |
| Prefs keys | `approval_mode`, `approval_allowlist` in `preferences.json` |
| Hook wire | `hooks/scripts/audit.py` PermissionRequest uses grade |

## Behavior (ACC soft layer only)

| Grade | ACC auto-allow |
|-------|----------------|
| `off` | Never |
| `ask` | Safe reads + safe bash prefixes (default spam-killer) |
| `allowlist` | Safe reads + shell matching `approval_allowlist` |
| `strict` | Never (+ extra caution copy) |

**Does not invent Codex APIs.** Host sandbox / approval policy stay Codex-owned (`/permissions`, config.toml). ACC grades only steer ACC hook soft auto-allow + plain hints. Hard PreToolUse denials still block every grade.

## Research (WEB)

| Product | Pattern | URL |
|---------|---------|-----|
| Cursor run modes | Allowlist → sandbox → classifier (Auto-review); strict = allowlist-only | https://forum.cursor.com/t/auto-review-run-mode/161922 |
| Cursor allowlist + sandbox | Run mode docs / security writeups | https://www.totalum.app/blog/cursor-auto-review-totalum |
| Windsurf/Devin terminal auto-exec | Disabled / Allowlist Only / Auto / Turbo + allow/deny lists | https://docs.devin.ai/desktop/terminal |
| Windsurf JetBrains levels | Off / Auto / Turbo | https://docs.devin.ai/windsurf/plugins/cascade/cascade-overview |
| Codex sandbox + approvals | Two layers; Auto = workspace-write + on-request | https://developers.openai.com/codex/agent-approvals-security |
| Codex permission modes | Ask for approval / Auto-review / Full access | https://developers.openai.com/codex/permission-modes |
| Codex hooks | PermissionRequest allow/deny or leave host prompt | https://developers.openai.com/codex/hooks |

Local Codex mirror used:

```bash
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" --show hooks
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" --show agent-approvals
python3 "/home/mitun/anyonecancode development/codex docs/read-docs.py" --show permission-modes
```

## Checks run

```bash
python3 -m pytest \
  plugins/anyone-can-code/tests/test_approval_grades.py \
  plugins/anyone-can-code/tests/test_approval_spam.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  -q
```

**Result:** 31 passed.

Focused grades:

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_approval_grades.py -q
```

**Result:** 20 passed.

CLI smoke:

```bash
python3 plugins/anyone-can-code/scripts/approval_grades.py --help
python3 plugins/anyone-can-code/scripts/approval_grades.py --describe strict
```

Skill budget: `SKILL.md` ≈ 1904 chars (under doctor 4000).

## Manual (user)

1. `$approval-mode` → shows grade + plain words.
2. Set `strict` → Read no longer ACC-auto-allows (Codex may still prompt).
3. Set `allowlist` + entries → only listed shell prefixes auto-allow.
4. Confirm Codex `/permissions` unchanged by ACC.

## Not in this lane

- No push / merge
- No rewrite of user `config.toml` or host approval_policy
- No Cursor/Windsurf API integration — UX analog only
