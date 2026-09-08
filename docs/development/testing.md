# Testing

Status: current for 0.6.0

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

The suite contains semantic/workflow tests, monitor debounce and recovery tests, plus MCP SDK v2 integration tests. The real stdio test starts
`python -m gamemaker_graph.mcp_server`, lists all tools, calls a tool, and checks structured output. Skill and
plugin validators are separate release gates documented in the root README.

Gameplay acceptance is not part of Python tests. A real Maker project also requires the runtime and human
evidence described in [TapTap Maker loop](../validation/taptap-maker-loop.md).
