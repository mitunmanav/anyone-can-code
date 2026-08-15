# Proof: feature/dr-subagent-roster

**Branch:** `feature/dr-subagent-roster`  
**Date:** 2026-08-03  
**Author:** Mitun only  
**Scope:** `$roster` — suggest Codex subagent roles as prompts only  
**Push/merge:** none

## Docs first (WEB + Codex)

### Codex Subagents
- Built-ins: `default`, `worker`, `explorer`.
- Custom agents: standalone TOML under `~/.codex/agents/` or `.codex/agents/`.
- Required fields: `name`, `description`, `developer_instructions`.
- Skill/AGENTS can request delegation; spawn is literal / explicit for most levels.
- Prefer parallel for read-heavy work; careful with parallel writes.
- Source: Codex Subagents docs (read-docs + learn.chatgpt.com agent-configuration/subagents).

### Copilot custom agent profiles (analog)
- Markdown agent profiles (`.github/agents/*.md` or `*.agent.md`) with YAML
  frontmatter: name, description, prompt, optional tools/MCP.
- Same idea as role prompts — host-specific format.
- ACC does **not** write Copilot profiles or Codex TOML; `$roster` suggests
  paste-ready Codex spawn prompts only.

## Delivered

| Item | Path |
|------|------|
| Skill | `plugins/anyone-can-code/skills/roster/SKILL.md` |
| UI / policy | `plugins/anyone-can-code/skills/roster/agents/openai.yaml` |
| Helper | `plugins/anyone-can-code/scripts/subagent_roster.py` |
| Tests | `plugins/anyone-can-code/tests/test_subagent_roster.py` |
| EXPECTED map | `tests/test_skill_display_names.py` → `"ACC roster"` |
| Explicit-only | `tests/test_skill_discovery.py` → `roster` in `EXPLICIT_ONLY` |

## Behavior

1. Default roles: **explorer** (read-only built-in), **worker** (read-write built-in), **reviewer** (read-only prompt role).
2. Each card has paste-ready `Spawn a subagent` block (Job / Scope / Expected / caveman).
3. Optional `toml_snippet` text for user paste into `.codex/agents/` — helper never writes.
4. `allow_implicit_invocation: false` (explicit `$roster` only).
5. CLI: `--json`, `--goal`, `--scope`, `--roles`.

## Evidence

```text
python3 -m pytest plugins/anyone-can-code/tests/test_subagent_roster.py \
  plugins/anyone-can-code/tests/test_skill_display_names.py \
  plugins/anyone-can-code/tests/test_skill_discovery.py \
  plugins/anyone-can-code/tests/test_ship_set.py \
  plugins/anyone-can-code/tests/test_skill_path_contract.py -q
# 24 passed, 35 subtests passed

python3 -m pytest plugins/anyone-can-code/tests -q
# 592 passed, 2 skipped, 122 subtests passed
```

Skill budget: `SKILL.md` = **2141** chars (limit 4000).

CLI smoke:

```bash
python3 plugins/anyone-can-code/scripts/subagent_roster.py --json --goal "review auth" --scope "src/auth/"
# count=3; explorer/worker/reviewer spawn prompts filled
```

## How to re-check

```bash
python3 -m pytest plugins/anyone-can-code/tests/test_subagent_roster.py -q
python3 plugins/anyone-can-code/scripts/subagent_roster.py --roles explorer,reviewer --goal "map login"
# → paste-ready prompts only; no .codex/agents written
```

## PASS/FAIL

**PASS** — helper + skill registration + full suite green. No push. No merge.
