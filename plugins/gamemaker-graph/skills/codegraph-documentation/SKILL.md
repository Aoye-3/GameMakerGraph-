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

1. Check GameGraph status. Rebuild its disposable index when it is missing or stale and that local derived-file write is within the task scope.
2. Query GameGraph for the project overview and the feature or system being documented.
3. Use `gamegraph context` for the combined gameplay/document/code seed. Ask CodeGraph directly for deeper architecture, entry points, callers, dependencies, and tests only when the deliverable needs them.
4. Inspect the source files that support important claims. Ask the user only when creative intent, product policy, or an architecture decision cannot be established from sources.
5. Select the smallest document set justified by the repository. Read [references/document-system.md](references/document-system.md) when choosing or structuring multiple documents.
6. Create or update local Markdown documents. Preserve existing conventions and links; do not overwrite confirmed design statements with graph inference.
7. Cross-link gameplay concepts to scenes/data/assets and to their implementing modules or symbols. Record source paths and important unresolved relationships.
8. Re-query affected graph areas, check local links, and report what is source-confirmed, inferred, missing, or stale.

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
