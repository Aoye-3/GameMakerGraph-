# CodeGraph Source Analysis and Integration Decision

## Scope and identity

This review targets [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph), because its
`codegraph_explore` and `codegraph_node` tools match the CodeGraph rules installed in this workspace. It is not
the separate `codegraph-ai/CodeGraph` project that an earlier README link referenced.

Local verification on 2026-09-07 used CodeGraph `1.1.6` and Node `24.13.1`.

## Source architecture

The upstream repository describes a deterministic, local-first pipeline:

```text
files
  → ExtractionOrchestrator / tree-sitter
  → SQLite nodes, edges and files
  → ReferenceResolver
  → GraphQueryManager / GraphTraverser
  → ContextBuilder
  → CLI, MCP and library consumers
```

The important source boundaries are:

- `src/index.ts`: public `CodeGraph` façade for init/open/index/sync/search/context/impact/watch;
- `src/extraction/`: native Rust/tree-sitter extraction, per-language rules and worker parsing;
- `src/db/`: SQLite schema, WAL-backed connection and FTS5 queries;
- `src/resolution/`: import, name, inheritance, framework route and dynamic-boundary resolution;
- `src/graph/`: traversal, call paths, impact radius and shared graph derivations;
- `src/context/`: bounded Markdown/JSON context rendering;
- MCP/CLI surfaces: thin consumers of the same public graph operations.

Sources: [upstream architecture notes](https://github.com/colbymchenry/codegraph/blob/main/CLAUDE.md),
[upstream README](https://github.com/colbymchenry/codegraph/blob/main/README.md).

## What CodeGraph already solves

CodeGraph extracts functions, classes, methods, imports and code relationships; resolves calls, imports,
inheritance and framework-specific routes; stores them in `.codegraph/codegraph.db`; and incrementally updates
the index. Its default MCP surface intentionally centers on `codegraph_explore`, while `node`, `search`,
`callers`, `callees`, `impact`, `files` and `status` remain available or have CLI equivalents.

Source: [official MCP reference](https://github.com/colbymchenry/codegraph/blob/main/site/src/content/docs/reference/mcp-server.md).

Rebuilding this inside GameMakerGraph would duplicate the most expensive and least game-specific work: language
grammars, symbol identity, cross-file resolution, framework special cases, incremental synchronization and code
context ranking.

## What GameMakerGraph adds

GameMakerGraph owns relationships CodeGraph cannot infer reliably from syntax alone:

- confirmed gameplay intent and player-facing rules;
- design document headings and references;
- scenes, resources, data, assets and UI slots;
- mapping from a gameplay concept to its implementation and verification evidence;
- missing-document and document/implementation drift checks;
- lightweight direction discussion that preserves human confirmation.

The graphs overlap at files but not at responsibility. CodeGraph answers how code flows; GameMakerGraph answers
why a game behavior exists and which non-code production artifacts participate.

## Integration options considered

### Copy or fork upstream

Rejected. The MIT license permits modification and redistribution, but a fork would require keeping attribution
and continuously absorbing parser, resolver and platform changes. None of that differentiates GameMakerGraph.

Source: [CodeGraph MIT license](https://github.com/colbymchenry/codegraph/blob/main/LICENSE).

### Embed the npm library

Deferred. The library API is capable, but it would add a Node runtime/package boundary to a dependency-free
Python Core. Upstream documents Node requirements for direct embedding, whereas its bundled CLI already provides
the required operations.

### Public CLI Provider

Selected for `0.2`. `status`, `query`, `impact` and `files` expose JSON. GameMakerGraph can normalize those values,
gracefully handle missing/stale indexes, and keep its own Core independent. A later MCP adapter can implement the
same contract when GameMakerGraph runs inside a host that exposes CodeGraph tools directly.

## Live compatibility probe

Against this repository, CodeGraph `1.1.6` indexed 5 Python files into 63 nodes and 134 edges. Querying
`build_graph` returned its function node and related imports; depth-2 impact included `rebuild_graph`, the CLI
entry point and relevant tests. These shapes became fixtures for `CodeGraphProvider` tests.

## Operational cautions

- The CodeGraph index is derived and local; never treat SQLite as a shared product database.
- CLI-only use should check `pendingChanges`; automatic synchronization depends on its watcher/MCP lifecycle.
- GameMakerGraph must not auto-install or auto-initialize CodeGraph on a user's project.
- CodeGraph documents optional anonymous usage telemetry and opt-out controls. Installation and telemetry choice
  remain the user's responsibility. See [upstream telemetry policy](https://github.com/colbymchenry/codegraph/blob/main/TELEMETRY.md).
- JSON compatibility is protected by our normalizer, not by assuming upstream internal schemas are permanent.

## Decision

Integrate and acknowledge CodeGraph; do not fork it. Product-specific tuning belongs in GameMakerGraph's query
composition, node mapping, documentation Skill and future MCP adapter. Upstream parser or resolver improvements
should be consumed through released interfaces rather than copied into this repository.
