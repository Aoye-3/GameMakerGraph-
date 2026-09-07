---
name: game-quality-review
description: Review a completed game slice across code quality, performance, documentation alignment, runtime evidence, and player experience. Use after implementation or for a focused optimization/review request; not to implement fixes or to accept a feature from file existence alone.
---

# Game Quality Review

Review claims and player-visible outcomes, not effort or tool success.

1. Prefer `gamegraph_inspect_project` and `gamegraph_query` to verify current memory and inspect the
   implemented feature. Do not rebuild before review when the stale baseline is needed to compare changes.
2. Review code correctness and maintainability separately from performance. Give measured or source-backed
   optimization opportunities; do not label speculative micro-optimizations as required work.
3. Compare project documents and implementation sources. Flag stale rules, unmapped systems, missing
   tests, broken links, and unresolved assumptions.
4. For runtime claims, require evidence from the current implementation: launch/run identity, input or
   action trace, observable state, player-visible capture where relevant, and diagnostics from the same run.
5. Review overall experience as hypotheses: clarity, controls, feedback, pacing, visual consistency, and
   narrative continuity. When actual player behavior, notes, traces, captures, or diagnostics exist, read
   [references/playtest.md](references/playtest.md). Prioritize player evidence over a generic score.
6. Call `gamegraph_review_increment` with project-relative evidence from the current run. Return one result
   per claim: supported, failed, or insufficient evidence. Show the deterministic maintenance plan, and
   call `gamegraph_apply_maintenance` only after explicit user confirmation; then rebuild the index.

Do not blindly apply every third-party review suggestion, claim that a screenshot proves hidden state, or
edit the project while acting solely as reviewer.
