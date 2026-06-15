# fn-16-enforce-acc-workflow-ownership-across.1 Contain specialist workflow takeover before and after use

## Description
Reproduce and fix workflow takeover from specialist skill process rules. Exact real-use pattern: user asks ACC to use brainstorming/product-design/UI skills; specialist process adds its own plan, approval gate, visual companion/browser offer, or workflow controls before ACC loads project preferences. Add deterministic pre-work ownership contract and recursive post-result containment while preserving bounded technical output.
## Acceptance
- [ ] Exact specialist-request wording keeps ACC owner and does not imply handoff.
- [ ] Route carries pre-work workflow contract and project-preference-first rule.
- [ ] Specialist assignment limits actions and forbids process takeover.
- [ ] Nested takeover controls are detected and reported by exact path.
- [ ] Bounded technical output is preserved.
- [ ] Browser/server/visual companion attempts are contained unless allowed by ACC and user.
- [ ] Explicit exact user handoff still works.
- [ ] Full tests, compile, Doctor, Flow, and diff integrity pass.
- [ ] Repo docs and Obsidian brain are updated.
## Done summary
Implemented ACC workflow ownership enforcement before and after specialist use. Every route carries workflow contract. Specialist mentions do not imply handoff. Assignments require project context first and advisory process authority. Recursive containment removes nested foreign workflow controls while preserving bounded technical output. Exact explicit user handoff remains supported.
## Evidence
- Commits:
- Tests: 7 focused workflow takeover tests passed, 108 full plugin tests passed, Python compileall passed, Doctor 34 PASS, 0 WARN, 0 FAIL, Flow validation 0 errors, 0 warnings, git diff --check passed
- PRs: