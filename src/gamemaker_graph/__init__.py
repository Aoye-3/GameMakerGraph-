"""GameMakerGraph public package."""

from .codegraph import CodeGraphProvider
from .context import impact_graph, task_context
from .docs import check_docs, init_docs, inspect_docs, suggest_docs
from .graph import (
    build_graph,
    graph_overview,
    graph_status,
    rebuild_graph,
    search_graph,
)

__all__ = [
    "CodeGraphProvider",
    "build_graph",
    "check_docs",
    "graph_overview",
    "graph_status",
    "impact_graph",
    "init_docs",
    "inspect_docs",
    "rebuild_graph",
    "search_graph",
    "suggest_docs",
    "task_context",
]

__version__ = "0.3.0"
