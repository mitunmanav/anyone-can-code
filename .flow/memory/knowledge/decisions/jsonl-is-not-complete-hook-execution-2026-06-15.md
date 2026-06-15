---
title: JSONL is not complete hook execution evidence
date: "2026-06-15"
track: knowledge
category: decisions
module: ACC hook observability / fn-14
tags: [important, deferred, hooks, jsonl, observability, fn-14]
applies_when: Auditing Codex sessions or claiming ACC hook execution/effectiveness
decision_status: accepted
alternatives_considered: [Treat system/developer messages as hook proof, Infer runs from timing, Use rollout JSONL as complete ledger]
---

## Important deferred finding

Existing Codex rollout JSONL files cannot reconstruct complete hook execution history. `HookStarted`, `HookCompleted`, warnings, hook names, run counts, status, and duration are intentionally not persisted. System prompts, normal developer messages, collaboration-mode messages, and plugin capability injections are never hook proof.

JSONL may prove only a distinctive persisted hook effect, such as known `additionalContext`, changed tool input/result, hook warning, block, or hook-owned durable artifact. Direct scan of 16 supplied session JSONLs found no identifiable persisted hook effect.

Do not reopen this as a JSONL extraction problem unless new source evidence appears. Resume later through `fn-14-make-acc-hooks-effective-from-non-git`: capture live app-server hook events, optional consented local OTLP metrics, and ACC-owned correlated receipts. Old silent runs remain unrecoverable from retained JSONL alone.

Priority: IMPORTANT. Status: DEFERRED by user; return later.
