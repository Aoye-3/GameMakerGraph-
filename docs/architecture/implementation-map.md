# Implementation Map

Status: current for 0.5.0

| Concept | Implementation | Verification |
| --- | --- | --- |
| Controlled semantic facts and stable IDs | `src/gamemaker_graph/semantic.py` | `tests/test_semantic.py` |
| Artifact plus semantic graph | `src/gamemaker_graph/graph.py` | `tests/test_graph.py`, `tests/test_semantic.py` |
| Revision-safe six-tool workflow | `src/gamemaker_graph/workflow.py` | `tests/test_workflow.py` |
| MCP SDK v2 stdio adapter | `src/gamemaker_graph/mcp_server.py` | `tests/test_mcp_server.py` |
| Existing Core CLI | `src/gamemaker_graph/cli.py` | `tests/test_cli.py` |
| Optional CodeGraph provider | `src/gamemaker_graph/codegraph.py` | `tests/test_codegraph_provider.py` |
| Project documentation templates | `src/gamemaker_graph/docs.py` | `tests/test_docs_framework.py` |
| TapTap Maker readiness helpers | `src/gamemaker_graph/trial.py` | `tests/test_trial.py` |

All paths are repository-relative. Code symbols are resolved by direct source inspection unless a current
CodeGraph index proves symbol relationships.
