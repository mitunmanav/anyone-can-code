# Proof: EFFICIENCY mode (feature/dr-efficiency)

**Date:** 2026-08-03  
**Branch:** `feature/dr-efficiency`  
**Goal:** Cheap + fast ACC inject without dropping honesty.

## Codex docs first

Topics read via `codex docs/read-docs.py`:

| Topic | Why |
|-------|-----|
| `hooks` | SessionStart inject budget; keep all 10 hooks |
| `skills` | `$efficiency` skill layout + progressive load |
| `models` | Model suggestions only — no host picker APIs |

## Honest limits

- ACC **suggests** cheaper model labels (ledger + soft tip).
- GPT-5.6 family spirit labels: **Sol** full · **Terra** mid · **Luna** cheap.
- ACC **never forces** Codex host model picker APIs we do not control.
- Efficiency may trade optional Tier C (host/loops/obs parade), verbose empty receipts, fat inject.
- Efficiency must **not** trade: goal/NOW memory core, fail-closed gates, proof rules, ENFORCE comm.

## Sources that turn efficiency ON

1. `ACC_EFFICIENCY=1|true|yes`
2. `ACC_LOAD_LEAN=1|true|yes` (legacy lean; unified)
3. Prefs `lean: true` or `efficiency: true` in  
   `.codex/anyone-can-code/settings/preferences.json`

## Implementation map

| Piece | Path |
|-------|------|
| Pure flags | `plugins/anyone-can-code/scripts/efficiency_mode.py` |
| Session inject | `plugins/anyone-can-code/hooks/scripts/load_session.py` |
| Soft model tip | `plugins/anyone-can-code/scripts/model_ledger.py` (`efficiency=True`) |
| Guard lean host skip | `plugins/anyone-can-code/hooks/scripts/guard.py` |
| Skill | `plugins/anyone-can-code/skills/efficiency/` |
| Settings note | `plugins/anyone-can-code/skills/settings/SKILL.md` |
| Tests | `plugins/anyone-can-code/tests/test_efficiency_mode.py` |

## Caps

| Mode | Soft inject cap |
|------|-----------------|
| Normal | 5500 chars |
| Efficiency / lean | 3200 chars |

Tier A always. Tier B if room. Tier C only when efficiency **off**.

## Hooks count

Must stay **10** event keys in `hooks/hooks.json` (no Superpowers empty hooks).

## Verify commands

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_efficiency_mode.py \
  plugins/anyone-can-code/tests/test_load_session.py \
  plugins/anyone-can-code/tests/test_model_ledger.py -q

python3 plugins/anyone-can-code/scripts/efficiency_mode.py --project-root .

python3 -m json.tool plugins/anyone-can-code/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/anyone-can-code/hooks/hooks.json >/dev/null
```

## Result

- pytest (`test_efficiency_mode` + `test_load_session` + `test_model_ledger`): **PASS** (23)
- hooks count: **10**
- soft tip language present: **yes** (ledger `tip` + skill + inject banner)
- Codex topics: hooks / skills / models (read first)
