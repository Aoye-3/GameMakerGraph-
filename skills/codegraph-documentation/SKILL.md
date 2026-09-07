---
name: codegraph-documentation
description: Build or update source-backed local technical documentation by combining GameMakerGraph gameplay/project relationships with CodeGraph code structure. Use for architecture, frontend, backend, gameplay implementation, setup, testing, or delivery documentation; not for ordinary code lookup with no documentation deliverable.
---

# CodeGraph Documentation

Build a documentation system that lets a general coding agent move from gameplay intent to its concrete code implementation without scanning the whole repository.

## Source hierarchy

Use both views when available:

- GameMakerGraph supplies project type, gameplay documents, scenes, assets, data, explicit file references, and freshness.
- CodeGraph supplies symbols, imports, calls, implementations, tests, and code-level impact.
- Native project files remain the source of truth. Treat graph results as derived evidence, not as permission to invent missing design intent.

When `.codegraph/` and CodeGraph tools are available, prefer architecture exploration first and specific symbol/file lookup second. If CodeGraph is unavailable, state that code-level relationships are based on direct file inspection and do not claim a verified call graph.

## Workflow

1. Prefer `gamegraph_inspect_project` and `gamegraph_query`; use the equivalent CLI only when the MCP is unavailable. Rebuild the disposable index when it is missing or stale and that write is in scope.
2. Before implementation, use `gamegraph_prepare_increment` for the confirmed goal. Keep its document and acceptance suggestions as candidates until the user confirms them.
3. Use the MCP query result for the combined gameplay/document/code seed. Ask CodeGraph directly for deeper architecture, entry points, callers, dependencies, and tests only when the deliverable needs them.
4. Inspect the source files that support important claims. Ask the user only when creative intent, product policy, or an architecture decision cannot be established from sources.
5. Select the smallest document set justified by the repository. Read [references/document-system.md](references/document-system.md) when choosing or structuring multiple documents.
6. Create or update human-owned Markdown only when requested. For post-implementation project-memory maintenance, call `gamegraph_review_increment`, show the exact plan, and call `gamegraph_apply_maintenance` only after explicit user confirmation.
7. Cross-link gameplay concepts to scenes/data/assets and to their implementing modules or symbols. Record source paths and important unresolved relationships.
8. After an approved maintenance apply, call `gamegraph_rebuild_index`, re-query affected areas, check local links, and report what is source-confirmed, inferred, missing, or stale.

## Documentation rules

- Prefer a navigable documentation index over isolated files.
- Separate current architecture from plans and proposed decisions.
- Create frontend, backend, deployment, or operations documents only when those components exist.
- Keep setup and delivery steps executable and repository-specific.
- Use relative Markdown links and stable repository paths. Name concrete symbols when CodeGraph proves them.
- Include a compact `Sources` or `Implementation map` section where it materially helps future Agent retrieval.
- Do not generate a complete GDD for a small project by default.
- Never present inferred gameplay, story, art direction, or player experience as user-confirmed fact.

## Completion

Return the documents changed, the GameGraph areas and CodeGraph symbols used, unresolved gaps, and the checks performed. A documentation set is complete only when an Agent can follow links from a gameplay/system concept to its relevant implementation and verification entry points.
