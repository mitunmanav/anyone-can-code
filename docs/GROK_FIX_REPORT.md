# GROK FIX REPORT — Fable items (branch `grok`)

Author: Mitun · Worktree: `.worktrees/grok` only · No merge · No push  
Date: 2026-07-16  
Fable source: `docs/FABLE_REVIEW.md`  
Codex docs re-read before edits: `python3 "codex docs/read-docs.py" --show /codex/hooks` and `--show /codex/skills`

## Test results (this fix pass)

| Package | Command | Result |
|---------|---------|--------|
| Desktop | `python3 -m pytest plugins/anyone-can-code/tests -q` | **507 passed, 3 skipped, 67 subtests** |
| CLI | `python3 -m pytest plugins/anyone-can-code-cli/tests -q` | **510 passed, 3 skipped, 97 subtests** |

Packages kept in sync for shared Python + skill wording. Desktop/CLI `hooks.json` still differ by design (PowerShell vs `python3`/`commandWindows`); matchers both use `Bash|apply_patch`.

---

## Fable item → change → Codex doc → live path → test

### 1. BLOCKER — Security gate passes on empty scan

| | |
|--|--|
| **What changed** | `plugins/anyone-can-code/scripts/security_gate.py` (~159–176): if `files_scanned == 0`, set `ok = False` and FAIL message. Same file in CLI package. |
| **Codex doc** | Hooks: commands run in session cwd — wrong-root empty scans are realistic. Fail-closed product rule. |
| **Live path** | Hook `PreToolUse` → `guard.security_gate_for_deploy` → `security_gate.scan_project`; skill `$verify` deploy gate; CLI `python scripts/security_gate.py`. |
| **Test** | `tests/test_security_gate.py::test_empty_scan_is_not_pass`; existing deploy-deny tests still pass. |

### 2. GAP — Hook matchers `Edit\|Write` without canonical `apply_patch`

| | |
|--|--|
| **What changed** | `plugins/anyone-can-code/hooks/hooks.json` and CLI copy: PreToolUse / PostToolUse / PermissionRequest matcher → `Bash\|apply_patch` (3 places each package). |
| **Codex doc** | Hooks matcher table: tool names include `Bash`, `apply_patch` (Edit/Write are aliases only). Canonical name is `apply_patch`. |
| **Live path** | Bundled plugin hooks fire on Bash and file edits via `apply_patch`. |
| **Test** | `tests/test_hook_matchers.py::test_tool_events_match_bash_and_apply_patch` |

**Note:** Current Codex docs say `Edit`/`Write` *can* match `apply_patch` as aliases. Fable still correctly wanted the **canonical** name present so file edits are not dependent on alias quirks. We use `Bash|apply_patch`.

### 3. GAP — Skills used `$PLUGIN_ROOT` (hooks-only env)

| | |
|--|--|
| **What changed** | `hooks/scripts/load_session.py` (~183–193): SessionStart injects `ACC_PLUGIN_ROOT=…` from `PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / plugin layout. Skills (`status`, `verify`, `help`, `settings`, `handoff`, `resume`, `plan`, `orchestrator`) now call `python3 "<ACC_PLUGIN_ROOT>/scripts/…"` and state PLUGIN_ROOT is hooks-only. Desktop + CLI skills synced. |
| **Codex doc** | Hooks → Plugin-bundled hooks: `PLUGIN_ROOT` set for **hook commands** only. Skills docs do not give agent-shell `PLUGIN_ROOT`. |
| **Live path** | Hook `SessionStart` (`load_session.build_context`); skills use injected path. |
| **Test** | `tests/test_load_session.py::test_session_context_includes_loops_and_plugin_root` |

### 4. GAP — Dead duplicate guard handlers (drift risk)

| | |
|--|--|
| **What changed** | Removed unused `handle_user_prompt_submit` and `handle_pre_tool_use` from `hooks/scripts/guard.py` (Desktop + CLI). Live path remains `handle_payload` only. |
| **Codex doc** | Hooks call one command script; no dual entrypoint required. |
| **Live path** | `guard.main` → `handle_payload` only. |
| **Test** | Existing `test_guard.py` PreToolUse / UserPromptSubmit paths via `handle_payload`. |

### 5. GAP — “4000 char skill budget” framed as Codex limit

| | |
|--|--|
| **What changed** | `scripts/doctor.py`: `SKILL_BODY_HOUSE_BUDGET_CHARS = 4000` (ACC house rule), `CODEX_SKILLS_LIST_BUDGET_CHARS = 8000` (Codex list). Doctor PASS/FAIL text names both and says 4000 is **not** the Codex list limit. `tests/test_locked_guards.py` docstring corrected. CLI doctor synced. |
| **Codex doc** | Skills: initial skills list ≤ 2% of context **or 8,000 characters** when unknown — applies to **names + descriptions list**, not per-file SKILL.md body. Full SKILL.md still loads when selected. |
| **Live path** | CLI `python scripts/doctor.py` skill budget check. |
| **Test** | `tests/test_token_budget.py`, `tests/test_locked_guards.py` (house body budget still 4000). |

### 6. NOT SHIPPED → fixed — loop_registry was import-proof only

| | |
|--|--|
| **What changed** | `hooks/scripts/load_session.py` (~195–211): calls `list_loops()`, builds live `Loops: work=on, scheduled=opt-in, …` line into SessionStart context (uses return value; not discarded). Still also exposed via CLI + `$status`. |
| **Codex doc** | Hooks SessionStart `additionalContext` / plain developer context. |
| **Live path** | SessionStart hook; `$status` → `loop_registry.py` CLI; CLI main. |
| **Test** | `tests/test_load_session.py::test_session_context_includes_loops_and_plugin_root`; `tests/test_loop_registry.py`. |

### 7. NOTE — 1200-char turn context truncates safety lines

| | |
|--|--|
| **What changed** | `hooks/scripts/guard.py` `build_turn_context` + new `_join_body_and_safety` (~171–269): body may shrink; **safety lines** (rate-limit, interop, browser, host) reserved and always kept within budget. |
| **Codex doc** | UserPromptSubmit `additionalContext` injection (hooks). No Codex max of 1200 — ACC soft cap kept for token hygiene. |
| **Live path** | UserPromptSubmit → `guard.build_turn_context`. |
| **Test** | `tests/test_guard.py::test_safety_lines_never_truncated_when_body_is_huge` |

---

## Not fixed (and why)

| Item | Why left open |
|------|----------------|
| **session_self_learn** still only CLI-main / loop menu text | Loop registry now surfaces `self_improve=opt-in` and native path in menu; auto-running self-learn on SessionStart would write/scan without user opt-in (registry says opt-in). Full hook auto-call deferred. |
| **Guard outer `except: print({})` = allow** | Changing to fail-closed on every hook crash can brick sessions if state/path resolution fails. Needs careful design + Mitun GO. Fail-closed already holds **inside** `security_gate_for_deploy`. |
| **Pinned “approval chain / token-burn scope / session-scan scope”** | Not re-litigated in this pass; not in the three explicit bullets. Rate-limit still injected as safety line. Separate pass if Fable still flags them. |
| **expand_pack / new_pack thin** | Honest thin wrappers; no fattening. |
| **CODEX_RESEARCH_PLAN** | Plan only; Mitun chose **A — do nothing** on research ideas. |
| **Hooks not a full security wall** | Codex docs: PreToolUse is a guardrail, not complete enforcement. Documented limit, not fixed by more matchers. |
| **Live install smoke** | Still operator: trust hooks, confirm `ACC_PLUGIN_ROOT` appears on SessionStart, run one `$status` script path. |

---

## How Fable can re-check (no merge)

```bash
cd ".worktrees/grok"   # fence
git branch --show-current   # must be grok

# Empty scan must FAIL
python3 -c "
from pathlib import Path
import sys, tempfile
sys.path.insert(0, 'plugins/anyone-can-code/scripts')
import security_gate
r = security_gate.scan_project(Path(tempfile.mkdtemp()))
assert r['ok'] is False and r['files_scanned'] == 0
print('empty-scan FAIL ok')
"

# Matchers
python3 -c "
import json
from pathlib import Path
for pkg in ['anyone-can-code','anyone-can-code-cli']:
  h=json.loads(Path(f'plugins/{pkg}/hooks/hooks.json').read_text())
  for ev in ['PreToolUse','PostToolUse','PermissionRequest']:
    m=h['hooks'][ev][0]['matcher']
    assert m=='Bash|apply_patch', (pkg,ev,m)
print('matchers ok')
"

python3 -m pytest plugins/anyone-can-code/tests -q
python3 -m pytest plugins/anyone-can-code-cli/tests -q
```

---

## Claim check

| Claim | Evidence |
|-------|----------|
| Empty security scan is not PASS | `security_gate.py` + `test_empty_scan_is_not_pass` |
| File-edit hooks use Codex tool name | `hooks.json` matcher `Bash\|apply_patch` + `test_hook_matchers` |
| Skills do not rely on agent-shell PLUGIN_ROOT alone | SessionStart `ACC_PLUGIN_ROOT` + skill wording |
| Safety turn lines survive 1200 budget | `_join_body_and_safety` + `test_safety_lines_never_truncated_when_body_is_huge` |
| 4000 is ACC house body budget; Codex list is 8000 | doctor messaging + skills docs |
| loop_registry is a real SessionStart caller | `list_loops()` result in context + test |
| No merge / no push | This report only; Mitun decides |

MERGE-READY: **for Mitun only after Fable re-check** — Grok does not merge.
