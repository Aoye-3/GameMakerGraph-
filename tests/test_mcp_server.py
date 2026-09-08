import json
import sys
from pathlib import Path

import anyio
from mcp import Client, StdioServerParameters

from gamemaker_graph.mcp_server import server
from gamemaker_graph.workflow import PROJECT_MEMORY

TOOL_NAMES = {
    "gamegraph_inspect_project",
    "gamegraph_prepare_increment",
    "gamegraph_confirm_increment",
    "gamegraph_query",
    "gamegraph_review_increment",
    "gamegraph_apply_maintenance",
    "gamegraph_rebuild_index",
}


def _project(root: Path) -> None:
    (root / "scripts").mkdir()
    (root / "scripts/game.js").write_text("export const score = 0;", encoding="utf-8")
    memory = root / PROJECT_MEMORY
    memory.parent.mkdir(parents=True)
    memory.write_text(
        "# Project Memory\n\n<!-- GAMEGRAPH:START -->\n```json\n"
        '{"nodes": [], "edges": [], "applied_plans": []}\n'
        "```\n<!-- GAMEGRAPH:END -->\n",
        encoding="utf-8",
    )


def test_in_process_client_discovers_schemas_annotations_and_results(tmp_path: Path) -> None:
    _project(tmp_path)

    async def exercise() -> None:
        async with Client(server) as client:
            listed = await client.list_tools()
            tools = {tool.name: tool for tool in listed.tools}
            assert set(tools) == TOOL_NAMES
            assert set(tools["gamegraph_prepare_increment"].input_schema["required"]) == {
                "project_root",
                "goal",
            }
            assert tools["gamegraph_prepare_increment"].annotations.read_only_hint is True
            assert tools["gamegraph_confirm_increment"].annotations.read_only_hint is False
            assert tools["gamegraph_apply_maintenance"].annotations.read_only_hint is False
            assert tools["gamegraph_apply_maintenance"].annotations.destructive_hint is False
            assert tools["gamegraph_apply_maintenance"].annotations.idempotent_hint is True
            assert tools["gamegraph_apply_maintenance"].annotations.open_world_hint is False

            rebuilt = await client.call_tool(
                "gamegraph_rebuild_index", {"project_root": str(tmp_path)}
            )
            assert rebuilt.structured_content["status"] == "current"

            prepared = await client.call_tool(
                "gamegraph_prepare_increment",
                {"project_root": str(tmp_path), "goal": "Collect a star"},
            )
            confirmed = await client.call_tool(
                "gamegraph_confirm_increment",
                {
                    "project_root": str(tmp_path),
                    "expected_revision": prepared.structured_content["revision"],
                    "draft": prepared.structured_content["facts"]["draft"],
                },
            )
            assert confirmed.structured_content["status"] == "confirmed"

            failed = await client.call_tool(
                "gamegraph_inspect_project", {"project_root": str(tmp_path / "missing")}
            )
            assert failed.structured_content["status"] == "error"
            assert set(failed.structured_content) == {
                "schema_version",
                "operation",
                "status",
                "project_root",
                "revision",
                "facts",
                "warnings",
                "next_actions",
            }

    anyio.run(exercise)


def test_real_stdio_subprocess_lists_and_calls_tools(tmp_path: Path) -> None:
    _project(tmp_path)
    config = tmp_path / ".maker-mcp/config.json"
    config.parent.mkdir()
    config.write_text('{"token":"STDIO-SECRET"}', encoding="utf-8")

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gamemaker_graph.mcp_server"],
        )
        async with Client(parameters) as client:
            listed = await client.list_tools()
            assert {tool.name for tool in listed.tools} == TOOL_NAMES
            result = await client.call_tool(
                "gamegraph_inspect_project", {"project_root": str(tmp_path)}
            )
            assert result.structured_content["operation"] == "gamegraph_inspect_project"
            assert "STDIO-SECRET" not in json.dumps(result.structured_content)

    anyio.run(exercise)
