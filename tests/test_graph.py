import json
from pathlib import Path

from gamemaker_graph.graph import (
    build_graph,
    graph_overview,
    graph_status,
    rebuild_graph,
    search_graph,
)


def _write_project(root: Path) -> None:
    (root / "docs").mkdir()
    (root / "scenes").mkdir()
    (root / "scripts").mkdir()
    (root / "assets").mkdir()
    (root / "project.godot").write_text(
        '[application]\nrun/main_scene="res://scenes/main.tscn"\n', encoding="utf-8"
    )
    (root / "docs" / "gameplay.md").write_text(
        "# Core Loop\n\nThe player collects stars.\n\nSee [main scene](../scenes/main.tscn).\n",
        encoding="utf-8",
    )
    (root / "scenes" / "main.tscn").write_text(
        '[gd_scene]\n[ext_resource path="res://scripts/player.gd" type="Script" id="1"]\n',
        encoding="utf-8",
    )
    (root / "scripts" / "player.gd").write_text("var stars := 0\n", encoding="utf-8")
    (root / "assets" / "player.png").write_bytes(b"png")


def test_build_connects_documents_headings_and_native_references(tmp_path: Path) -> None:
    _write_project(tmp_path)

    graph = build_graph(tmp_path)
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {(edge["source"], edge["target"], edge["kind"]) for edge in graph["edges"]}

    assert graph["project_type"] == "godot"
    assert nodes["file:docs/gameplay.md"]["kind"] == "document"
    assert nodes["heading:docs/gameplay.md#core-loop"]["label"] == "Core Loop"
    assert nodes["file:scenes/main.tscn"]["kind"] == "scene"
    assert ("file:docs/gameplay.md", "file:scenes/main.tscn", "links_to") in edges
    assert ("file:scenes/main.tscn", "file:scripts/player.gd", "references") in edges


def test_graph_is_deterministic_and_index_does_not_index_itself(tmp_path: Path) -> None:
    _write_project(tmp_path)

    first = rebuild_graph(tmp_path)
    first_graph = json.loads((tmp_path / ".gamemakergraph/graph.json").read_text("utf-8"))
    second = rebuild_graph(tmp_path)
    second_graph = json.loads((tmp_path / ".gamemakergraph/graph.json").read_text("utf-8"))

    assert first["revision"] == second["revision"]
    assert first_graph == second_graph
    assert not any(".gamemakergraph" in node["source"] for node in second_graph["nodes"])


def test_status_reports_missing_current_and_stale(tmp_path: Path) -> None:
    _write_project(tmp_path)
    assert graph_status(tmp_path)["status"] == "missing"

    rebuild_graph(tmp_path)
    assert graph_status(tmp_path)["status"] == "current"

    (tmp_path / "scripts/player.gd").write_text("var stars := 1\n", encoding="utf-8")
    assert graph_status(tmp_path)["status"] == "stale"


def test_overview_and_search_are_bounded_and_work_without_godot(tmp_path: Path) -> None:
    (tmp_path / "design.md").write_text("# Shop Economy\n\nCoins buy upgrades.\n", "utf-8")
    rebuild_graph(tmp_path)

    overview = graph_overview(tmp_path)
    results = search_graph(tmp_path, "shop", limit=1)

    assert overview["project_type"] == "generic"
    assert overview["status"] == "current"
    assert overview["node_kinds"]["document"] == 1
    assert len(results["results"]) == 1
    assert results["results"][0]["source"] == "design.md"


def test_hidden_and_dependency_directories_are_ignored(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / ".secret").mkdir()
    (tmp_path / ".secret/note.md").write_text("hidden", "utf-8")
    (tmp_path / "node_modules/pkg").mkdir(parents=True)
    (tmp_path / "node_modules/pkg/index.js").write_text("ignored", "utf-8")

    graph = build_graph(tmp_path)

    sources = {node["source"] for node in graph["nodes"]}
    assert ".secret/note.md" not in sources
    assert "node_modules/pkg/index.js" not in sources
