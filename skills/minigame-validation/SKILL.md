---
name: minigame-validation
description: Prepare and run a bounded minigame validation with GameMakerGraph and an existing game-development MCP, initially TapTap Maker. Use when the user wants to prove the local development loop end to end; not for publishing, broad game production, or claiming success without a live provider and current runtime evidence.
---

# Minigame Validation

Prove that project understanding, documentation, implementation, and live verification work together.

1. Run `gamegraph trial status <project> --provider taptap-maker`. If the Maker project is not initialized,
   stop before writing. Read [references/taptap-maker.md](references/taptap-maker.md) and request approval
   before installation, login, remote project creation, checkout, build, upload, or publish.
2. For an initialized project, run `gamegraph trial prepare`, then `gamegraph trial plan`. Confirm one
   primary player verb, one observable state change, one goal, and explicit exclusions with the user.
3. Verify the current Agent session is connected to the intended Maker project using the provider's live
   status capability. A local config marker or CLI installation is not a connection proof.
4. Use the existing Maker MCP as the executor. Keep the implementation to one playable loop and update
   the project documents and implementation map as code, data, and assets become real.
5. Run the real preview/runtime. Prove launch, input-to-state change, goal, restart, and zero blocking
   diagnostics with evidence tied to the same current run.
6. Rebuild GameGraph after final changes and verify documentation sources match the current revision.
7. Report each acceptance claim as supported, failed, or insufficient evidence. Leave publishing outside
   this validation unless the user separately authorizes it.

Do not use a fake provider for final acceptance. Do not substitute file existence, generated assets, a
successful MCP call, or build success for a playable result.
