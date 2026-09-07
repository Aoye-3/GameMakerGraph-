---
name: game-project-exploration
description: Explore an existing local game project and return a bounded, source-backed project or feature map before implementation. Use when an Agent needs to understand gameplay, scenes, assets, documents, code entry points, tests, or likely change impact; not for editing or open-ended design discussion.
---

# Game Project Exploration

Build the smallest reliable context needed for the next development decision.

1. Run `gamegraph status <project>`. Rebuild the disposable graph when it is missing or stale and the
   task permits derived local writes.
2. Use `gamegraph overview`, then `gamegraph context <query> <project>` for the requested feature.
3. Use `gamegraph impact` before proposing changes. When CodeGraph is available, use its architecture
   and symbol relations for callers, dependencies, implementations, and tests.
4. Inspect the native files behind important graph claims. Treat graph results as derived evidence;
   native project files remain authoritative.
5. Return: project purpose, relevant gameplay/system concepts, source files and symbols, assets/data,
   tests, likely change surface, stale or missing relationships, and the smallest question that blocks
   implementation.

Keep exploration bounded to the request. Mark product or creative meaning as confirmed, inferred, or
unknown. Do not edit code, invent gameplay intent, or claim that a dynamic dependency is covered when
only static evidence exists.
