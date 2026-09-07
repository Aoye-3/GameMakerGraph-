import json
from pathlib import Path

from gamemaker_graph.graph import build_graph
from gamemaker_graph.semantic import parse_semantic_documents


def _controlled(payload: dict[str, object]) -> str:
    return (
        "# Project memory\n\nHuman notes stay here.\n\n"
        "<!-- GAMEGRAPH:START -->\n"
        "```json\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n```\n<!-- GAMEGRAPH:END -->\n"
    )


def test_semantic_facts_are_extracted_only_from_controlled_markdown_blocks(
    tmp_path: Path,
) -> None:
    (tmp_path / "outside.md").write_text(
        '# Notes\n\n{"nodes":[{"key":"outside","kind":"feature","label":"Ignore"}]}',
        encoding="utf-8",
    )
    memory = tmp_path / "docs/project-memory.md"
    memory.parent.mkdir()
    memory.write_text(
        _controlled(
            {
                "nodes": [
                    {"key": "dash", "kind": "feature", "label": "Dash"},
                    {"key": "move", "kind": "player_action", "label": "Move"},
                ],
                "edges": [
                    {"source": "move", "target": "dash", "kind": "depends_on"}
                ],
                "applied_plans": [],
            }
        ),
        encoding="utf-8",
    )

    semantic = parse_semantic_documents(tmp_path)

    assert {node["details"]["key"] for node in semantic["nodes"]} == {"dash", "move"}
    assert len(semantic["edges"]) == 1
    assert "outside" not in json.dumps(semantic)


def test_semantic_ids_stay_stable_when_a_label_changes(tmp_path: Path) -> None:
    memory = tmp_path / "memory.md"
    payload = {
        "nodes": [{"key": "core-loop", "kind": "feature", "label": "First label"}],
        "edges": [],
        "applied_plans": [],
    }
    memory.write_text(_controlled(payload), encoding="utf-8")
    first_id = parse_semantic_documents(tmp_path)["nodes"][0]["id"]

    payload["nodes"][0]["label"] = "Renamed label"
    memory.write_text(_controlled(payload), encoding="utf-8")
    second_id = parse_semantic_documents(tmp_path)["nodes"][0]["id"]

    assert first_id == second_id


def test_graph_keeps_artifacts_and_adds_semantic_nodes_and_evidence(tmp_path: Path) -> None:
    script = tmp_path / "scripts/player.js"
    script.parent.mkdir()
    script.write_text("export function move() {}", encoding="utf-8")
    evidence = tmp_path / "evidence/playtest.md"
    evidence.parent.mkdir()
    evidence.write_text("Player completed the loop.", encoding="utf-8")
    memory = tmp_path / "docs/project-memory.md"
    memory.parent.mkdir()
    memory.write_text(
        _controlled(
            {
                "nodes": [
                    {"key": "move", "kind": "player_action", "label": "Move"},
                    {
                        "key": "move-playtest",
                        "kind": "validation_evidence",
                        "label": "Move playtest",
                        "path": "evidence/playtest.md",
                    },
                ],
                "edges": [
                    {"source": "move", "target": "scripts/player.js", "kind": "implemented_by"},
                    {
                        "source": "move",
                        "target": "move-playtest",
                        "kind": "validated_by",
                    },
                ],
                "applied_plans": [],
            }
        ),
        encoding="utf-8",
    )

    graph = build_graph(tmp_path)

    kinds = {node["kind"] for node in graph["nodes"]}
    assert {"script", "document", "player_action", "validation_evidence"} <= kinds
    evidence_node = next(node for node in graph["nodes"] if node["kind"] == "validation_evidence")
    assert evidence_node["details"]["path"] == "evidence/playtest.md"
    assert not Path(evidence_node["details"]["path"]).is_absolute()
    assert {edge["kind"] for edge in graph["edges"]} >= {"implemented_by", "validated_by"}


def test_invalid_semantic_relationship_is_warned_and_not_indexed(tmp_path: Path) -> None:
    memory = tmp_path / "memory.md"
    memory.write_text(
        _controlled(
            {
                "nodes": [
                    {"key": "proof", "kind": "validation_evidence", "label": "Proof"},
                    {"key": "feature", "kind": "feature", "label": "Feature"},
                ],
                "edges": [
                    {"source": "proof", "target": "feature", "kind": "implemented_by"}
                ],
                "applied_plans": [],
            }
        ),
        encoding="utf-8",
    )

    semantic = parse_semantic_documents(tmp_path)

    assert semantic["edges"] == []
    assert any("Invalid semantic relationship" in warning for warning in semantic["warnings"])
