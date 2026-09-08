---
name: game-art-direction
description: Plan consistent game art, character variants, UI placeholders, and replaceable asset slots before image generation or integration. Use when a game needs visual direction or a batch asset plan; not for generating assets without an approved reference or for judging personal taste as fact.
---

# Game Art Direction

Turn visual intent into a replaceable, reviewable asset plan.

1. For an existing project, prefer `gamegraph_query` for current asset and feature context, then establish
   concise style keywords, visual mood, target platform, readability constraints, and one or
   more user-approved references. Prefer analyzing an actual reference over relying on broad style labels.
2. Produce one standard draft before batch generation. Do not generate a full set until the user approves
   the composition, palette, silhouette, line/texture treatment, and content boundaries.
3. Define stable asset slots and exact technical constraints: role, dimensions, transparency, states,
   frame count, pivot/trim, filename, target path, provenance, and license.
4. For UI, reserve exact-size placeholders early so code and layout can proceed before final art. Keep
   later replacement possible without changing gameplay logic.
5. Generate character states and related variants from the same approved reference; do not independently
   reinterpret each image. Typical slots may include silhouette, portrait, avatar, state variants, item
   icon, dialogue nameplate, and observation/clue display, but only include slots the game actually uses.
6. Review images for consistency, player readability, accidental discomfort, and prompt/style drift.
   Ask the creator to approve subjective choices. After assets are actually integrated and observed in the
   running game, use `gamegraph_review_increment` with the confirmed `increment_id` to preview traceable memory changes; do not apply them
   without confirmation.

Never treat a successful image generation call as an integrated asset, and never silently substitute a
placeholder when a required asset fails review.
