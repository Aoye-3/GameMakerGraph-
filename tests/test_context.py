from pathlib import Path

from gamemaker_graph.context import impact_graph, task_context
from gamemaker_graph.graph import rebuild_graph


def _write_connected_project(root: Path) -> None:
    (root / "docs").mkdir()
    (root / "scenes").mkdir()
    (root / "scripts").mkdir()
    (root / "docs/gameplay.md").write_text(
        "# Core Loop\n\nCollect stars in the [main scene](../scenes/main.tscn).\n",
        encoding="utf-8",
    )
    (root / "scenes/main.tscn").write_text(
        '[gd_scene]\n[ext_resource path="res://scripts/player.gd" type="Script"]\n',
        encoding="utf-8",
    )
    (root / "scripts/player.gd").write_text("var stars := 0\n", encoding="utf-8")


def test_task_context_returns_a_bounded_source_backed_neighborhood(tmp_path: Path) -> None:
    _write_connected_project(tmp_path)
    rebuild_graph(tmp_path)

    result = task_context(tmp_path, "core loop", depth=2, limit=10, include_code=False)
    node_ids = {node["id"] for node in result["nodes"]}

    assert result["status"] == "current"
    assert result["blocked"] is False
    assert "file:docs/gameplay.md" in node_ids
    assert "heading:docs/gameplay.md#core-loop" in node_ids
    assert "file:scenes/main.tscn" in node_ids
    assert "file:scripts/player.gd" in node_ids
    assert len(result["nodes"]) <= 10
    assert all(node["source"] for node in result["nodes"])


def test_task_context_refuses_to_use_a_stale_gamegraph(tmp_path: Path) -> None:
    _write_connected_project(tmp_path)
    rebuild_graph(tmp_path)
    (tmp_path / "scripts/player.gd").write_text("var stars := 1\n", encoding="utf-8")

    result = task_context(tmp_path, "stars", include_code=False)

    assert result["status"] == "stale"
    assert result["blocked"] is True
    assert result["nodes"] == []


def test_impact_walks_semantic_edges_without_expanding_every_project_file(
    tmp_path: Path,
) -> None:
    _write_connected_project(tmp_path)
    (tmp_path / "scripts/unrelated.gd").write_text("var weather := 'sunny'\n", encoding="utf-8")
    rebuild_graph(tmp_path)

    result = impact_graph(
        tmp_path,
        "file:scenes/main.tscn",
        depth=1,
        include_code=False,
    )
    node_ids = {node["id"] for node in result["nodes"]}

    assert node_ids == {
        "file:docs/gameplay.md",
        "file:scenes/main.tscn",
        "file:scripts/player.gd",
    }
    assert {edge["kind"] for edge in result["edges"]} == {"links_to", "references"}
