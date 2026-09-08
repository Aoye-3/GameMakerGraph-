---
name: game-project-bootstrap
description: Prepare an existing or newly initialized game project for structured local development by defining scope, decomposing systems, and creating only the minimum source-backed documentation. Use at project start or before a substantial feature; not for routine bug fixes or for generating a full GDD by default.
---

# Game Project Bootstrap

Make the project controllable before implementation without turning a small game into a studio process.

1. Establish the intended player outcome, platform, smallest playable loop, explicit exclusions, and
   observable completion criteria. Keep unresolved creative facts under `To confirm`.
2. Prefer `gamegraph_inspect_project`, then `gamegraph_prepare_increment` for the smallest playable
   goal. Its facts and acceptance items are a preview; after user confirmation, persist the exact draft with
   `gamegraph_confirm_increment`. Use `gamegraph docs suggest`
   and `docs init` only when the MCP is unavailable or the user explicitly wants missing templates;
   initialization must preserve existing files.
3. Decompose only independently testable systems. For each module, record responsibility, dependency,
   implementation sources, and verification; avoid one oversized requirements document.
4. Start implementation from the smallest vertical slice. Guide the coding Agent progressively from
   basic interaction to harder technical points, and keep data/state inspectable when that materially
   helps tuning or debugging.
5. After implementation, use `gamegraph_review_increment`; show its maintenance plan before calling
   `gamegraph_apply_maintenance`. After confirmation and apply, verify the automatic rebuild and ensure
   project overview, gameplay rules, implementation map, setup, and testing entry points link to real sources.

The developer remains responsible for product direction. Do not fabricate a world, plot, art style,
team process, delivery date, or architecture decision to make a template look complete.
