# Ready-Made Automations

Optional. Codex Desktop runs these on a schedule in the background. Results land in the
**Triage** inbox in the sidebar; runs with nothing to report auto-archive.

Plugin install first: see the [root README](../../../README.md).

**Setup (once per automation):** Codex app sidebar → Automations → New →
paste a prompt below → pick the schedule → choose your project.
Safety: these prompts only read your project — keep the default read-only
sandbox. No extra installs needed.

### 1. Daily project recap (schedule: every morning)

```
Read .codex/anyone-can-code/state/session-snapshot.md and state-current.md in
this project. Report 3 lines max: 1) where the project stands, 2) the next
step, 3) anything waiting on the user. If state is unchanged since the last
run, archive with nothing to report.
Speak caveman style: simple, short, direct, no ceremony.
```

### 2. Stuck-task nudge (schedule: daily, afternoon)

```
Read .codex/anyone-can-code/state/state-current.md in this project. If the
"Updated" timestamp is older than 2 days and next step is not "done", report
one line: "Stuck since <date>. Next step was: <step>. Open the project and
run $resume." Otherwise archive with nothing to report.
Speak caveman style: simple, short, direct, no ceremony.
```

### 3. Weekly memory digest (schedule: weekly, e.g. Sunday)

```
Read the newest files in .codex/anyone-can-code/memory/notes/ in this project.
Report max 5 bullets: lessons recorded this week, duplicates you noticed, and
one suggestion for what to clean up. Do NOT modify any files — report only.
If no new notes this week, archive with nothing to report.
Speak caveman style: simple, short, direct, no ceremony.
```

## Notes

- Machine must be on and Codex running at the scheduled time (official docs).
- For Git projects you can run automations on a worktree to isolate changes;
  these three never write, so local read-only mode is fine.
- Custom cadence: choose "custom schedule" and enter cron syntax in the app.
