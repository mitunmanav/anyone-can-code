# ACC CLI Blind Proof

Strict-blind proof that **Anyone Can Code** works on **Codex CLI**.

- Model: **gpt-5.4-mini** · reasoning **low** (see `scenarios.json`)
- No `$skill` names in prompts · no coaching
- Medium app story: **local Python habit tracker**
- Scoreboard: every feature row **PASS / FAIL / NOT PROVEN**

Design: [DESIGN.md](./DESIGN.md) · Plan: [PLAN.md](./PLAN.md)

## Prerequisites

- `codex` on PATH
- ACC plugin installed + hooks trusted (or isolated `CODEX_HOME` — **must be written in PROOF**)
- Python 3

If home config is broken (e.g. duplicate `model_providers.headroom`), use:

```bash
export CODEX_HOME=/path/to/isolated/codex-home
python3 docs/proof/cli-blind/run_proof.py --run-id demo --codex-home "$CODEX_HOME"
```

## Commands

```bash
# From repo worktree root (.worktrees/grok)
python3 docs/proof/cli-blind/run_proof.py --dry-parse
python3 -m pytest docs/proof/cli-blind/tests -q
python3 docs/proof/cli-blind/run_proof.py --run-id $(date +%Y%m%d-%H%M%S)
# subset:
python3 docs/proof/cli-blind/run_proof.py --run-id smoke --scenarios S1,S7
```

Artifacts (gitignored): `docs/proof/cli-blind/artifacts/<run-id>/`

- `PROOF.md` — overall + env honesty + matrix
- `scoreboard.md`
- `project/` — habit tracker tree
- `sessions/` — stdout/stderr per try

## How to read scores

| Status | Meaning |
|--------|---------|
| PASS | Evidence path/log exists |
| FAIL | Feature wrong (e.g. safety ran curl\|bash) |
| NOT PROVEN | Never seen after retries — **honest gap** |

Overall PASS needs: core product, SessionStart+Stop, memory write+recall, safety not FAIL-open.  
It does **not** require 21/21 skills.

## Honesty

- Prompts only in `scenarios.json` (guarded by tests).
- Always disclose sandbox / bypass / isolated home in `PROOF.md`.
- Do not commit secrets or full live artifacts.

## Public sample (redacted)

- [PROOF.public.md](./samples/PROOF.public.md) — no personal paths  
- [scoreboard.public.md](./samples/scoreboard.public.md)
