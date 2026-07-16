# ACC Wiring Report

Branch: `grok` · Worktree only · Author: Mitun  
Purpose: prove each helper has a **live product path** (hook / skill / CLI), not tests alone.  
Someone who did not watch the build should be able to re-check every claim below.

---

## OpenSpec pattern (applied before wiring)

From https://github.com/Fission-AI/openspec (README + docs/how-commands-work + customization + superpowers-bridge style):

1. **Do not edit the foreign tool** — wrap at instruction/binding layer.
2. **Phase → skill bindings** with PRECHECK (present + healthy).
3. **Output redirect** into ACC-owned paths (not `docs/superpowers/*`).
4. **ACC remains workflow owner**; external skills are advisory.
5. **Fail loud / ACC fallback** when a skill is missing.
6. Prefer strong execute path (subagent-driven) over weaker alternate.

ACC implementation: `scripts/front_door.py` → `tool_interop` schema `acc-tool-interop-v1`, plus `$bridge` / `$plan` / `$execute` / `$verify` skill text. Hooks inject a compact interop line on `UserPromptSubmit`.

---

## Codex docs read (for this work)

| Topic | How | Why |
|-------|-----|-----|
| Hooks | `python3 "codex docs/read-docs.py" --show /codex/hooks` | `UserPromptSubmit` / `SessionStart` `additionalContext`; timeout default 600s; `PLUGIN_ROOT`; PreToolUse is guardrail-only |
| Build skills | `--show /codex/skills` | Skill as product path; progressive disclosure; `$` invoke |
| Build plugins | `--show plugins/build` | Plugin layout, bundled hooks/skills, install cache |
| Skills & Plugins | `--show skills-and-plugins` | Skill vs plugin roles |
| Agent approvals | `--show agent-approvals-security` | Sandbox/approvals; hooks not full wall |

---

## What was wired: helper → live path → test

### A. Outside-tool interop (Superpowers-style)

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `front_door.build_tool_interop` | CLI: `python scripts/front_door.py "…"` returns `tool_interop`; skills `$bridge` `$plan` `$execute` `$verify`; hook `UserPromptSubmit` via `guard.build_tool_interop_line` | `tests/test_front_door.py` (interop + prefer subagent); `tests/test_guard.py` (`test_tool_interop_*`, turn context) |
| `capability_registry` | Used by front_door routing | front_door specialist/plugin route tests |
| Specialist intents + short-skill harden | front_door `choose_plugin_route` / `resolve_requested_specialists` | `test_short_skill_name_*`, `test_browser_word_alone_*` |

### B. Safety-critical

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `security_gate` | Hook `PreToolUse` via `guard.security_gate_for_deploy` (fail-closed on error); skill `$verify` | `tests/test_guard.py` deploy gate; security tests |
| `browser_policy` | Hook turn context when browser/QA keywords; CLI `python scripts/browser_policy.py`; skill `$verify` | `test_browser_policy_*` in `test_guard.py`; `test_browser_policy.py`; `test_browser_qa.py` |
| `safety_receipts` | Skill `$execute` (risky work rules) | `test_project_state.py` safety gate cases; `test_system_integration.py` |
| `silent_failure_detector` | Hook `PostToolUse` / permission audit path (`hooks/scripts/audit.py`) | silent failure tests / audit pipeline |
| Desktop hook `timeout: 30` | `hooks/hooks.json` every command hook | `tests/test_desktop_hooks_timeout.py` |

### C. Session / host / loops / observability

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `host_detect` | Hook `UserPromptSubmit` (`guard.build_host_detect_line`); `SessionStart` (`load_session.build_context`); CLI `python scripts/host_detect.py --guidance`; skills `$status` `$help` | `test_host_detect_line_*`; host_detect unit tests |
| `loop_registry` | SessionStart context; CLI `python scripts/loop_registry.py`; skill `$status` | `test_loop_registry.py`; load_session imports list_loops |
| `session_self_learn` | Documented by loop_registry self_improve setup; CLI already has main | `test_loop_registry.py` references native; `test_session_self_learn.py` |
| `ai_observability` | SessionStart injects receipt; CLI `python scripts/ai_observability.py --project-root .`; skill `$status` | `test_ai_observability.py`; load_session path |
| `rate_limit_guard` | guard + load_session turn/session context | rate limit tests; guard context |
| `wiki_memory` | load_session wiki brief | `test_wiki_memory.py` |

### D. Execute / walk-away / git

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `walkaway_pack` | CLI `python scripts/walkaway_pack.py --goal`; skill `$execute` + `$status` | CLI main smoke; walkaway unit tests |
| `git_workflow` | CLI `python scripts/git_workflow.py --mode … --dry-run`; skill `$execute` | CLI main; `test_git_workflow.py` |
| `task_coordination` / `canonical_state` | skills `$plan` `$execute` | project state tests |

### E. Communication / settings

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `comm_contract` | CLI `python scripts/comm_contract.py …`; skill `$settings` dry-run | `test_comm_contract.py` |
| `front_door` / `memory_preflight` / `product_intake` | skills `$orchestrator` `$clarify` `$plan` | front_door + memory tests |

### F. Doctor / QA

| Helper | Live product path | Proving test |
|--------|-------------------|--------------|
| `doctor.run_tool_interop` | CLI `python scripts/doctor.py` | doctor PASS `verification/tool_interop` |
| `installed_runtime_qa` | doctor path | installed QA tests |
| `status_model` | doctor + product_intake | status model smoke |

### G. Packs still thinner (documented)

| Helper | Live product path | Status |
|--------|-------------------|--------|
| `expand_pack` | Has CLI main (`if __name__`); intended for host expand explain | Wired as CLI; skill call optional — not forced in skills (desktop/cli package already split) |
| `new_pack` | Library for modes/knobs; setup/settings consume concepts | Prefer `$settings` prefs; full new_pack CLI still light |

---

## Dual package (Desktop + CLI)

| Package | Path |
|---------|------|
| Desktop | `plugins/anyone-can-code/` |
| CLI | `plugins/anyone-can-code-cli/` |

Shared wiring was **copied** into both where logic is shared (hooks scripts, scripts, skills, tests).  
Hooks **shape** differs on purpose: Desktop PowerShell-encoded; CLI `python3 "$PLUGIN_ROOT/…"` + `commandWindows`.

pytest: root `pytest.ini` uses `--import-mode=importlib` so both packages can be tested together.

---

## How to re-check (manual, no live Codex UI required)

```bash
cd .worktrees/grok   # stay on branch grok only

# Interop
python3 plugins/anyone-can-code/scripts/front_door.py "use writing-plans for a feature" | head

# Safety browser
python3 plugins/anyone-can-code/scripts/browser_policy.py

# Host + loops + observability
python3 plugins/anyone-can-code/scripts/host_detect.py --guidance
python3 plugins/anyone-can-code/scripts/loop_registry.py
python3 plugins/anyone-can-code/scripts/ai_observability.py --project-root .

# Walk-away + git dry
python3 plugins/anyone-can-code/scripts/walkaway_pack.py --goal
python3 plugins/anyone-can-code/scripts/git_workflow.py --mode manual --dry-run

# Tone
python3 plugins/anyone-can-code/scripts/comm_contract.py caveman-strict "Feature implemented successfully."

# Doctor interop
python3 plugins/anyone-can-code/scripts/doctor.py 2>&1 | rg tool_interop

# Tests
python3 -m pytest plugins/anyone-can-code/tests -q
```

Hook product path (code-level): `hooks/scripts/guard.py` → `build_turn_context` includes interop + browser + host; `hooks/scripts/load_session.py` → host + loops + ai receipt.

---

## Issues found + fixes (harden)

| Issue | Fix | Commit family |
|-------|-----|----------------|
| Deploy security gate fails open on exception | Fail closed with plain reason | `fix(guard): fail closed…` |
| Desktop hooks missing timeout (docs default 600s) | `timeout: 30` on all Desktop hooks | `fix(hooks): set Desktop…` |
| tool_interop only if front_door skill runs | Inject interop line on UserPromptSubmit | `fix(guard): inject tool_interop…` |
| Short skill names (auth) steal routes | Whole-phrase + min length 8 | earlier interop + front_door tighten |
| Bare “browser” specialist | Narrow markers | `fix(front_door): tighten…` |
| Dual-package pytest basename clash | `pytest.ini` importlib addopts | `fix(test): …` |
| Doctor no explicit interop check | `run_tool_interop` | `fix(doctor): …` |
| Orphan helpers (test-only) | Hooks + skills + CLI mains (this report) | wiring commits |

---

## Still open / risky

1. **Hooks are not a complete enforcement wall** (Codex docs): `unified_exec` / some tools can bypass PreToolUse matchers. ACC remains best-effort guardrail.
2. **expand_pack / new_pack** not forced every turn — intentional; avoid fattening. CLI main exists for expand_pack; new_pack is mostly library.
3. **Live Desktop/CLI install smoke** is operator’s job (Mitun), not claimed green here.
4. **Plugin hooks need `/hooks` trust** after install (Codex docs).
5. **Skill char budget (4000)** is tight on execute/bridge — further skill text needs trims first.
6. **Silent `except: pass` in hooks** still used so hooks never crash the app; critical deploy path now fails closed.

---

## Product path vs test-only (plain)

| Class | Meaning |
|-------|---------|
| **Product path** | Hook fires in Codex session, or skill `$name` tells agent to run a script, or user/agent can run script as CLI with `__main__` |
| **Test-only** | Only `tests/test_*.py` import it — **forbidden as end state** for helpers we keep |

This report’s tables claim product path for each listed helper. Re-run the commands + pytest rows to verify.

