---
name: game-quality-review
description: Review a completed game slice across code quality, performance, documentation alignment, runtime evidence, and player experience. Use after implementation or for a focused optimization/review request; not to implement fixes or to accept a feature from file existence alone.
---

# Game Quality Review

Review claims and player-visible outcomes, not effort or tool success.

1. Rebuild or verify current GameGraph, then query the implemented feature and its impact surface.
2. Review code correctness and maintainability separately from performance. Give measured or source-backed
   optimization opportunities; do not label speculative micro-optimizations as required work.
3. Compare project documents and implementation sources. Flag stale rules, unmapped systems, missing
   tests, broken links, and unresolved assumptions.
4. For runtime claims, require evidence from the current implementation: launch/run identity, input or
   action trace, observable state, player-visible capture where relevant, and diagnostics from the same run.
5. Review overall experience as hypotheses: clarity, controls, feedback, pacing, visual consistency, and
   narrative continuity. Prioritize actual player feedback over a generic automated score.
6. Return one result per claim: supported, failed, or insufficient evidence. Recommend only the smallest
   bounded fixes with the highest user-visible value.

Do not blindly apply every third-party review suggestion, claim that a screenshot proves hidden state, or
edit the project while acting solely as reviewer.
