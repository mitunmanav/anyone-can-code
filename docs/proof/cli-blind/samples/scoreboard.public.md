# ACC CLI blind scoreboard

| row | kind | status | evidence | notes |
|-----|------|--------|----------|-------|
| setup | skill | NOT PROVEN |  |  |
| help | skill | NOT PROVEN |  |  |
| status | skill | NOT PROVEN |  |  |
| resume | skill | PASS | S2: skill read resume |  |
| verify | skill | PASS | S4: skill read verify |  |
| fix | skill | NOT PROVEN |  |  |
| onboard | skill | NOT PROVEN |  |  |
| clarify | skill | NOT PROVEN |  |  |
| plan | skill | NOT PROVEN |  |  |
| execute | skill | PASS | S1: skill read execute |  |
| learn | skill | NOT PROVEN |  |  |
| wiki | skill | NOT PROVEN |  |  |
| capture | skill | NOT PROVEN |  |  |
| govern | skill | NOT PROVEN |  |  |
| readable | skill | NOT PROVEN |  |  |
| handoff | skill | PASS | S4: handoff artifact seen; S5: handoff artifact seen; S6: handoff artifact seen; S7: handoff artifact seen; S8: handoff artifact seen |  |
| bridge | skill | NOT PROVEN |  |  |
| settings | skill | NOT PROVEN |  |  |
| update | skill | NOT PROVEN |  |  |
| usage | skill | NOT PROVEN |  |  |
| orchestrator | skill | NOT PROVEN |  |  |
| SessionStart | hook | PASS | S1: hook SessionStart; S2: hook SessionStart; S3: hook SessionStart; S4: hook SessionStart; S5: hook SessionStart; S6: hook SessionStart; S7: hook SessionStart; S8: hook SessionStart |  |
| UserPromptSubmit | hook | PASS | S1: hook UserPromptSubmit; S2: hook UserPromptSubmit; S3: hook UserPromptSubmit; S4: hook UserPromptSubmit; S5: hook UserPromptSubmit; S6: hook UserPromptSubmit; S7: hook UserPromptSubmit; S8: hook UserPromptSubmit |  |
| PreToolUse | hook | PASS | S1: hook PreToolUse; S2: hook PreToolUse; S3: hook PreToolUse; S4: hook PreToolUse; S7: hook PreToolUse; S8: hook PreToolUse |  |
| PermissionRequest | hook | NOT PROVEN |  |  |
| PostToolUse | hook | PASS | S1: hook PostToolUse; S2: hook PostToolUse; S3: hook PostToolUse; S4: hook PostToolUse; S8: hook PostToolUse |  |
| Stop | hook | PASS | S1: hook Stop; S2: hook Stop; S3: hook Stop; S4: hook Stop; S5: hook Stop; S6: hook Stop; S7: hook Stop; S8: hook Stop |  |
| PreCompact | hook | NOT PROVEN |  |  |
| SubagentStart | hook | NOT PROVEN |  |  |
| SubagentStop | hook | NOT PROVEN |  |  |
| PostCompact | hook | NOT PROVEN |  |  |
| doctor | other | PASS | doctor fail=0 pass=35 warn=7 |  |
| memory_write | other | PASS | S4: new notes ['~/anyonecancode development/.worktrees/grok/docs/proof/cli-blind/artifacts/live-20260723-112551/project/.codex/anyone-can-code/memory/notes/2026-07-23.md', '~/anyonecancode development/.worktrees/grok/docs/proof/cli-blind/artifacts/live-20260723-112551/project/.codex/anyone-can-code/memory/notes/project/d362637a-30e9-45e4-bc70-9f054bc69b23.md']; S5: new notes ['~/anyonecancode development/.worktrees/grok/docs/proof/cli-blind/artifacts/live-20260723-112551/project/.codex/anyone-can-code/memory/notes/auto-want-38871f2ba821f0cf.md'] |  |
| memory_recall | other | PASS | S6: stdout recalled preference |  |
| safety_curl_pipe | other | PASS | S7: PreToolUse blocked download piped shell |  |
| portable_handoff | other | PASS | S4: handoff file under .codex; S5: handoff file under .codex; S6: handoff file under .codex; S7: handoff file under .codex; S8: handoff file under .codex |  |
