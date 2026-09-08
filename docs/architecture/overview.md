# Architecture Overview

Status: current for 0.6.0

`semantic.py` parses confirmed Markdown facts. `graph.py` combines them with artifact nodes in a deterministic
derived index. `review_state.py` owns active-increment baselines and the debounced monitor. `workflow.py` owns
revision-safe inspect/prepare/confirm/query/review/apply/rebuild behavior.
`mcp_server.py` is a thin official SDK v2 adapter. Existing CLI, documentation framework, CodeGraph provider,
context queries, and Maker trial helpers remain available.

GameMakerGraph never calls CodeGraph internals or Maker MCP. The former is an optional public code Provider;
the latter is an independent executor and runtime-evidence provider.

## Sources

- [Implementation map](implementation-map.md)
- [Continuous memory](continuous-memory.md)
- [MCP contract](../contracts/mcp-tools.md)
