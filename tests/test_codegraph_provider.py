import json
import subprocess
from pathlib import Path
from typing import Any

from gamemaker_graph.codegraph import CodeGraphProvider
from gamemaker_graph.context import task_context
from gamemaker_graph.graph import rebuild_graph


def _runner(arguments: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
    command = arguments[1]
    if command == "status":
        output: Any = {
            "initialized": True,
            "version": "1.1.6",
            "fileCount": 5,
            "nodeCount": 63,
            "edgeCount": 134,
            "pendingChanges": {"added": 0, "modified": 0, "removed": 0},
        }
    elif command == "query":
        output = [
            {
                "node": {
                    "id": "function:abc",
                    "kind": "function",
                    "name": "build_graph",
                    "qualifiedName": "build_graph",
                    "filePath": "src/gamemaker_graph/graph.py",
                    "startLine": 155,
                    "signature": "(project_root: Path) -> dict[str, Any]",
                },
                "score": 99.0,
            }
        ]
    elif command == "impact":
        output = {
            "symbol": "build_graph",
            "depth": 2,
            "affected": [
                {
                    "name": "rebuild_graph",
                    "kind": "function",
                    "filePath": "src/gamemaker_graph/graph.py",
                    "startLine": 280,
                }
            ],
        }
    else:
        raise AssertionError(arguments)
    return subprocess.CompletedProcess(arguments, 0, json.dumps(output), "")


def test_codegraph_provider_normalizes_status_query_and_impact(tmp_path: Path) -> None:
    (tmp_path / ".codegraph").mkdir()
    provider = CodeGraphProvider(executable="codegraph", runner=_runner)

    context = provider.context(tmp_path, "build graph", limit=5)
    impact = provider.impact(tmp_path, "build_graph", depth=2)

    assert context["status"] == "current"
    assert context["version"] == "1.1.6"
    assert context["symbols"] == [
        {
            "id": "function:abc",
            "kind": "function",
            "name": "build_graph",
            "qualified_name": "build_graph",
            "source": "src/gamemaker_graph/graph.py",
            "line": 155,
            "signature": "(project_root: Path) -> dict[str, Any]",
            "score": 99.0,
        }
    ]
    assert impact["status"] == "current"
    assert impact["affected"][0]["name"] == "rebuild_graph"


def test_codegraph_provider_is_optional_when_not_installed_or_initialized(tmp_path: Path) -> None:
    unavailable = CodeGraphProvider(executable=None).context(tmp_path, "player")
    uninitialized = CodeGraphProvider(executable="codegraph", runner=_runner).context(
        tmp_path, "player"
    )

    assert unavailable["status"] == "unavailable"
    assert uninitialized["status"] == "uninitialized"


def test_task_context_combines_game_and_code_relationships(tmp_path: Path) -> None:
    (tmp_path / "design.md").write_text("# Graph Build\n\nBuild the project graph.\n", "utf-8")
    (tmp_path / ".codegraph").mkdir()
    rebuild_graph(tmp_path)
    provider = CodeGraphProvider(executable="codegraph", runner=_runner)

    result = task_context(tmp_path, "build graph", codegraph=provider)

    assert result["status"] == "current"
    assert result["codegraph"]["status"] == "current"
    assert result["codegraph"]["symbols"][0]["name"] == "build_graph"
