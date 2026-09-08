---
name: game-project-exploration
description: Explore an existing local game project and return a bounded, source-backed project or feature map before implementation. Use when an Agent needs to understand gameplay, scenes, assets, documents, code entry points, tests, or likely change impact; not for editing or open-ended design discussion.
---

# Game Project Exploration

Build the smallest reliable context needed for the next development decision.

1. Prefer `gamegraph_inspect_project`, then `gamegraph_query` for the requested feature. Rebuild the
   disposable graph with `gamegraph_rebuild_index` when it is missing or stale and derived local writes
   are in scope. Fall back to the equivalent `gamegraph` CLI only when the MCP is unavailable.
2. Before proposing an increment, call `gamegraph_prepare_increment` with the user's goal. Its questions
   and acceptance criteria are candidates only; after confirmation, pass the exact draft to
   `gamegraph_confirm_increment` before implementation.
3. Use the returned local facts and optional CodeGraph context to bound likely impact. When CodeGraph is
   available, use its architecture
   and symbol relations for callers, dependencies, implementations, and tests.
4. Inspect the native files behind important graph claims. Treat graph results as derived evidence;
   native project files remain authoritative.
5. Return: project purpose, relevant gameplay/system concepts, source files and symbols, assets/data,
   tests, likely change surface, stale or missing relationships, and the smallest question that blocks
   implementation.

Keep exploration bounded to the request. Mark product or creative meaning as confirmed, inferred, or
unknown. Do not edit code, invent gameplay intent, or claim that a dynamic dependency is covered when
only static evidence exists.
