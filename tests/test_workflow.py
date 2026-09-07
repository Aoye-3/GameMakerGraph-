import json
from pathlib import Path

import pytest

from gamemaker_graph.graph import graph_status, rebuild_graph
from gamemaker_graph.workflow import (
    _plan_id,
    apply_maintenance,
    inspect_project,
    prepare_increment,
    query_project,
    rebuild_index,
    review_increment,
)


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".gamemakergraph" not in path.parts
    }


def _project(root: Path) -> None:
    (root / "scripts").mkdir()
    (root / "scripts/game.js").write_text("export const score = 0;", encoding="utf-8")
    memory = root / "docs/development/project-memory.md"
    memory.parent.mkdir(parents=True)
    memory.write_text(
        "# Project Memory\n\nHuman-owned introduction.\n\n"
        "<!-- GAMEGRAPH:START -->\n```json\n"
        '{"nodes": [], "edges": [], "applied_plans": []}\n'
        "```\n<!-- GAMEGRAPH:END -->\n\nHuman-owned footer.\n",
        encoding="utf-8",
    )


def test_prepare_and_review_are_read_only_and_candidates_do_not_enter_graph(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    base_revision = graph_status(tmp_path)["revision"]
    before_prepare = _snapshot(tmp_path)

    prepared = prepare_increment(tmp_path, "让玩家收集一枚星星")

    assert prepared["status"] == "ready"
    assert _snapshot(tmp_path) == before_prepare
    graph_text = (tmp_path / ".gamemakergraph/graph.json").read_text("utf-8")
    assert "让玩家收集一枚星星" not in graph_text

    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")
    before_review = _snapshot(tmp_path)
    reviewed = review_increment(
        tmp_path,
        "让玩家收集一枚星星",
        base_revision,
        evidence=[
            {
                "path": "evidence/playtest.md",
                "kind": "playtest",
                "claim": "玩家实际收集星星后分数增加",
                "result": "passed",
            }
        ],
    )

    assert reviewed["status"] == "review_required"
    assert reviewed["facts"]["plan"]["plan_id"].startswith("plan:")
    assert _snapshot(tmp_path) == before_review


def test_apply_preserves_human_content_rejects_conflicts_and_is_idempotent(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    base_revision = graph_status(tmp_path)["revision"]
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")
    review = review_increment(tmp_path, "Add collectible", base_revision)
    plan = review["facts"]["plan"]
    expected = review["revision"]
    memory = tmp_path / "docs/development/project-memory.md"

    applied = apply_maintenance(tmp_path, expected, plan)
    first_bytes = memory.read_bytes()
    repeated = apply_maintenance(tmp_path, expected, plan)

    assert applied["status"] == "applied"
    assert repeated["status"] == "unchanged"
    assert memory.read_bytes() == first_bytes
    text = first_bytes.decode("utf-8")
    assert "Human-owned introduction." in text
    assert "Human-owned footer." in text
    assert graph_status(tmp_path)["status"] == "stale"

    rebuild_index(tmp_path)
    second_base = graph_status(tmp_path)["revision"]
    second_review = review_increment(tmp_path, "Add timer", second_base)
    (tmp_path / "scripts/game.js").write_text("export const score = 2;", encoding="utf-8")
    conflict = apply_maintenance(
        tmp_path, second_review["revision"], second_review["facts"]["plan"]
    )

    assert conflict["status"] == "conflict"
    assert second_review["facts"]["plan"]["plan_id"] not in memory.read_text("utf-8")


def test_all_workflow_results_use_the_envelope_and_never_expose_maker_config(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    config = tmp_path / ".maker-mcp/config.json"
    config.parent.mkdir()
    config.write_text('{"token":"TOP-SECRET-MAKER-TOKEN"}', encoding="utf-8")
    (tmp_path / "assets").mkdir()
    rebuild_index(tmp_path)

    results = [
        inspect_project(tmp_path),
        prepare_increment(tmp_path, "inspect goal"),
        query_project(tmp_path, "game", include_code=False),
        rebuild_index(tmp_path),
    ]

    required = {
        "schema_version",
        "operation",
        "status",
        "project_root",
        "revision",
        "facts",
        "warnings",
        "next_actions",
    }
    for result in results:
        assert required == set(result)
        assert "TOP-SECRET-MAKER-TOKEN" not in json.dumps(result)


def test_review_drops_evidence_paths_outside_the_project(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    base_revision = graph_status(tmp_path)["revision"]

    result = review_increment(
        tmp_path,
        "goal",
        base_revision,
        evidence=[{"path": str(tmp_path.parent / "secret.txt"), "claim": "invalid"}],
    )

    serialized = json.dumps(result)
    assert str(tmp_path.parent / "secret.txt") not in serialized
    assert any("evidence" in warning.lower() for warning in result["warnings"])


def test_rebuild_is_idempotent_and_query_exposes_stale_state(tmp_path: Path) -> None:
    _project(tmp_path)
    first = rebuild_index(tmp_path)
    second = rebuild_index(tmp_path)

    assert first["facts"]["changed"] is True
    assert second["facts"]["changed"] is False

    (tmp_path / "scripts/game.js").write_text("export const score = 3;", encoding="utf-8")
    stale = query_project(tmp_path, "score", include_code=False)

    assert stale["status"] == "stale"
    assert any("stale" in warning for warning in stale["warnings"])


def test_apply_rejects_a_hashed_plan_with_an_illegal_relationship(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    revision = graph_status(tmp_path)["revision"]
    plan = {
        "goal": "malicious",
        "base_revision": revision,
        "review_revision": revision,
        "document_changes": [
            {
                "path": "docs/development/project-memory.md",
                "nodes": [
                    {"key": "proof", "kind": "validation_evidence", "label": "Proof"},
                    {"key": "feature", "kind": "feature", "label": "Feature"},
                ],
                "edges": [
                    {"source": "proof", "target": "feature", "kind": "implemented_by"}
                ],
            }
        ],
    }
    plan["plan_id"] = _plan_id(plan)

    with pytest.raises(ValueError, match="relationship"):
        apply_maintenance(tmp_path, revision, plan)
