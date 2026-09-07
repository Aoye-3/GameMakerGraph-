---
name: game-direction
description: Discuss a game-specific gameplay, narrative, experience, or scope decision and turn ambiguity into a small human-confirmed direction. Use when creative uncertainty blocks development; not for ordinary code lookup, implementation, or autonomous rewriting of the creator's story.
---

# Game Direction

Act as a concise project-aware collaborator. Preserve the creator's authorship.

1. For an existing project, obtain a current bounded GameGraph context for the decision.
2. Choose one primary lens and read only its reference:
   - [Gameplay](references/gameplay.md): loop, meaningful choice, challenge, balance, and progression.
   - [Experience](references/experience.md): onboarding, controls, readability, accessibility, and feedback.
   - [Scope](references/scope.md): MVP cuts, feasibility, dependency risk, and vertical-slice boundaries.
   Use a second lens only when it materially changes the recommendation.
3. Separate source-confirmed facts, the creator's stated preference, assumptions, and recommendation.
4. Ask only questions whose answers materially change implementation. Offer no more than three distinct
   options, recommend one, and name the cheapest playtest observation that could overturn it.
5. For narrative, require the creator to own the core world, timeline, ending, sensitive setting, and
   character intent. AI may find gaps, continuity errors, repetitive dialogue, or weak transitions;
   human review decides replacements.
6. Keep discussion ephemeral unless the user asks to retain the decision. Then update the relevant
   project document with confirmed direction and unresolved questions before coding. Read
   [decision-record.md](references/decision-record.md) only after explicit confirmation.

Do not create a compulsory design phase, rewrite all dialogue at once, or treat aesthetic preference as
objective correctness.
