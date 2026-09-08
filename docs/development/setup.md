# Development Setup

Status: current for 0.6.0

Use Python 3.11+ and keep the virtual environment in the repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

Install pytest and Ruff in the same environment for development. The Core CLI remains usable after an editable
install without the MCP extra.

## Sources

- [`pyproject.toml`](../../pyproject.toml)
- [README installation](../../README.md#安装)
