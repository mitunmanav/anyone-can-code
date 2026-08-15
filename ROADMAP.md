# Roadmap

What is coming next in Anyone Can Code. Plain words, no dates. Plans can change — this is direction, not a promise.

**Product category:** reliability workflow plugin for OpenAI Codex — plan, build, resume, recover, verify. Not a new agent.

## Now — 2.0.0-beta.5 (open beta)

- **One plugin for Desktop + CLI.** Same marketplace entry (**Anyone Can Code**). Same version.
- **Offline auto memory on both hosts** when ACC hooks are trusted. Optional `$learn` / `$wiki` / `$capture` still work.
- **Host-honest.** Scheduled jobs and Sites stay Desktop host tools. CLI is not a fake Desktop UI.
- **Two-drawer memory.** Your taste lives in one global drawer. Project facts stay inside each project. Drawers never mix.
- **Lessons reload.** Project lessons can load in later sessions so known mistakes are less likely to repeat (not a hard guarantee).
- **Plain-words progress.** While building, ACC tells you what it is doing in simple words ("making the login page now… done").
- **Honest push-back.** If something is impossible, ACC says so. If there is a better way, it explains why in words you can check — not "trust me."
- **Safety guards baked in.** Empty security scans and deploy checks fail closed. Permanent tests keep the plugin small, simple, and dependency-free.
- **Verify before “done”.** Evidence-oriented completion records; built is not the same as verified.
- **CLI proof harness** is in the repo (`docs/proof/cli-blind/`). Live Desktop smoke is still a human check.

## Thinking about (later)

- **Plays-nice list.** Other plugins already work alongside ACC. Planned: an official list of tools we have tested that fit ACC's workflow without confusing it.
- **Smarter model choice.** Planned: learn which model and thinking level work for side tasks, then suggest instead of asking every time.
- **Stronger handoff at usage limits.** Planned: when a session hits a usage limit mid-work, progress and handoff are already saved so you can continue later. (Not guaranteed yet — that is the goal.)

## Have an idea?

Tell us in [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions) or on [Discord](https://discord.gg/qgS29y7TqP).
