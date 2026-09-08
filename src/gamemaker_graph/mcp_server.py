"""Official MCP SDK v2 stdio adapter for the GameMakerGraph workflow."""

from __future__ import annotations

from typing import Any, Callable

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from . import __version__
from .review_state import ReviewMonitor
from .workflow import (
    apply_maintenance,
    confirm_increment,
    error_envelope,
    inspect_project,
    prepare_increment,
    query_project,
    rebuild_index,
    review_increment,
)

SERVER_INSTRUCTIONS = """
GameMakerGraph maintains source-backed project memory and next-step navigation.
Before implementation, call gamegraph_prepare_increment and ask the user to confirm the proposed
scope and observable acceptance, then persist that exact draft with gamegraph_confirm_increment.
Use a separate engine or Maker MCP for implementation, building, running, and runtime evidence:
this server never calls another MCP. Project changes automatically mark the confirmed increment as
review_required. After implementation, call gamegraph_review_increment. Show its maintenance plan
to the user and call gamegraph_apply_maintenance only after explicit confirmation.
Never treat a build, screenshot, generated file, or tool call alone as proof that gameplay passed.
This server does not use Sampling and never confirms semantic documentation silently.
""".strip()

server = MCPServer(
    "gamemaker-graph",
    title="GameMakerGraph",
    description="Persistent local game-project memory and next-step navigation.",
    instructions=SERVER_INSTRUCTIONS,
    version=__version__,
)

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)
MAINTENANCE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)
MONITOR = ReviewMonitor()


def _call(
    operation: str,
    project_root: str,
    function: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    try:
        result = function()
        if result.get("status") != "error":
            MONITOR.register(project_root)
        return result
    except Exception as exc:  # MCP boundary: every result must retain the public envelope.
        return error_envelope(operation, project_root, exc)


@server.tool(title="Inspect game project", annotations=READ_ONLY)
def gamegraph_inspect_project(project_root: str) -> dict[str, Any]:
    """Inspect project docs, graph freshness, Maker marker, and optional CodeGraph status."""

    return _call(
        "gamegraph_inspect_project", project_root, lambda: inspect_project(project_root)
    )


@server.tool(title="Prepare game increment", annotations=READ_ONLY)
def gamegraph_prepare_increment(project_root: str, goal: str) -> dict[str, Any]:
    """Prepare source-backed context, questions, and acceptance candidates without writing."""

    return _call(
        "gamegraph_prepare_increment",
        project_root,
        lambda: prepare_increment(project_root, goal),
    )


@server.tool(title="Confirm game increment", annotations=MAINTENANCE)
def gamegraph_confirm_increment(
    project_root: str, expected_revision: str, draft: dict[str, Any]
) -> dict[str, Any]:
    """Persist one user-confirmed increment and establish its implementation baseline."""

    return _call(
        "gamegraph_confirm_increment",
        project_root,
        lambda: confirm_increment(project_root, expected_revision, draft),
    )


@server.tool(title="Query GameGraph", annotations=READ_ONLY)
def gamegraph_query(
    project_root: str, query: str, include_code: bool = True
) -> dict[str, Any]:
    """Query semantic/project facts and optionally combine the CodeGraph provider."""

    return _call(
        "gamegraph_query",
        project_root,
        lambda: query_project(project_root, query, include_code=include_code),
    )


@server.tool(title="Review game increment", annotations=READ_ONLY)
def gamegraph_review_increment(
    project_root: str,
    increment_id: str,
    evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare an increment and preview deterministic project-memory maintenance."""

    return _call(
        "gamegraph_review_increment",
        project_root,
        lambda: review_increment(project_root, increment_id, evidence or []),
    )


@server.tool(title="Apply confirmed memory maintenance", annotations=MAINTENANCE)
def gamegraph_apply_maintenance(
    project_root: str, expected_revision: str, plan: dict[str, Any]
) -> dict[str, Any]:
    """Apply one user-confirmed, revision-safe controlled Markdown plan."""

    return _call(
        "gamegraph_apply_maintenance",
        project_root,
        lambda: apply_maintenance(project_root, expected_revision, plan),
    )


@server.tool(title="Rebuild GameGraph index", annotations=MAINTENANCE)
def gamegraph_rebuild_index(project_root: str) -> dict[str, Any]:
    """Idempotently rebuild the disposable local index from project sources."""

    return _call(
        "gamegraph_rebuild_index", project_root, lambda: rebuild_index(project_root)
    )


def main() -> None:
    """Run the local server over stdio."""

    MONITOR.start()
    try:
        server.run(transport="stdio")
    finally:
        MONITOR.stop()


if __name__ == "__main__":
    main()
