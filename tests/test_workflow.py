import json
from pathlib import Path

import pytest

from gamemaker_graph.graph import graph_status, rebuild_graph
from gamemaker_graph.workflow import (
    _plan_id,
    apply_maintenance,
    confirm_increment,
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


def _confirm(root: Path, goal: str) -> dict:
    prepared = prepare_increment(root, goal)
    return confirm_increment(root, prepared["revision"], prepared["facts"]["draft"])


def test_prepare_is_read_only_and_confirmed_increment_survives_a_new_window(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    base_revision = graph_status(tmp_path)["revision"]
    before_prepare = _snapshot(tmp_path)

    prepared = prepare_increment(tmp_path, "让玩家收集一枚星星")

    assert prepared["status"] == "ready"
    draft = prepared["facts"]["draft"]
    assert draft["increment_id"].startswith("increment:")
    assert draft["base_revision"] == base_revision
    assert draft["player_observable_change"] == "让玩家收集一枚星星"
    assert draft["acceptance_criteria"]
    assert _snapshot(tmp_path) == before_prepare
    graph_text = (tmp_path / ".gamemakergraph/graph.json").read_text("utf-8")
    assert "让玩家收集一枚星星" not in graph_text

    confirmed = confirm_increment(tmp_path, base_revision, draft)
    inspected = inspect_project(tmp_path)

    assert confirmed["status"] == "confirmed"
    assert inspected["facts"]["active_increment"]["increment_id"] == draft["increment_id"]
    assert inspected["facts"]["review_state"]["status"] == "confirmed"
    assert inspected["facts"]["evidence_gaps"]
    assert "让玩家收集一枚星星" in (
        tmp_path / "docs/development/project-memory.md"
    ).read_text("utf-8")


def test_confirm_is_idempotent_and_revision_conflicts_are_zero_write(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    prepared = prepare_increment(tmp_path, "Add collectible")
    draft = prepared["facts"]["draft"]

    confirmed = confirm_increment(tmp_path, prepared["revision"], draft)
    memory = tmp_path / "docs/development/project-memory.md"
    first = memory.read_bytes()
    repeated = confirm_increment(tmp_path, prepared["revision"], draft)

    assert confirmed["status"] == "confirmed"
    assert repeated["status"] == "unchanged"
    assert memory.read_bytes() == first

    next_draft = prepare_increment(tmp_path, "Add timer")["facts"]["draft"]
    (tmp_path / "scripts/game.js").write_text("export const score = 2;", encoding="utf-8")
    conflicted = confirm_increment(tmp_path, next_draft["base_revision"], next_draft)

    assert conflicted["status"] == "conflict"
    assert memory.read_bytes() == first


def test_apply_preserves_human_content_rejects_conflicts_and_is_idempotent(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    confirmed = _confirm(tmp_path, "Add collectible")
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")
    review = review_increment(tmp_path, confirmed["facts"]["increment_id"])
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
    assert graph_status(tmp_path)["status"] == "current"
    assert applied["facts"]["review_state"] == "documented/current"

    second_confirmed = _confirm(tmp_path, "Add timer")
    (tmp_path / "scripts/game.js").write_text("export const score = 3;", encoding="utf-8")
    second_review = review_increment(tmp_path, second_confirmed["facts"]["increment_id"])
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
    confirmed = _confirm(tmp_path, "goal")
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")

    result = review_increment(
        tmp_path,
        confirmed["facts"]["increment_id"],
        evidence=[{"path": str(tmp_path.parent / "secret.txt"), "claim": "invalid"}],
    )

    serialized = json.dumps(result)
    assert str(tmp_path.parent / "secret.txt") not in serialized
    assert any("evidence" in warning.lower() for warning in result["warnings"])


def test_review_requires_playtest_or_user_confirmation_to_validate(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    confirmed = _confirm(tmp_path, "Add collectible")
    increment_id = confirmed["facts"]["increment_id"]
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")

    build_only = review_increment(
        tmp_path,
        increment_id,
        evidence=[{"kind": "build", "claim": "Build completed", "result": "passed"}],
    )
    validated = review_increment(
        tmp_path,
        increment_id,
        evidence=[
            {
                "kind": "playtest",
                "claim": "The player collected the item and score changed",
                "result": "passed",
                "revision": graph_status(tmp_path)["revision"],
            }
        ],
    )
    wrong_revision = review_increment(
        tmp_path,
        increment_id,
        evidence=[
            {
                "kind": "playtest",
                "claim": "Evidence from another build",
                "result": "passed",
                "revision": "sha256:older",
            }
        ],
    )

    assert build_only["facts"]["review_outcome"] == "implemented_unverified"
    assert build_only["facts"]["evidence_gaps"]
    assert any(item["type"] == "build_is_not_gameplay" for item in build_only["facts"]["findings"])
    assert validated["facts"]["review_outcome"] == "validated"
    assert validated["facts"]["evidence_gaps"] == []
    assert wrong_revision["facts"]["review_outcome"] == "implemented_unverified"

    state_after_review = inspect_project(tmp_path)["facts"]["review_state"]
    assert state_after_review["status"] == "implemented_unverified"


def test_new_change_after_review_invalidates_the_pending_plan(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    confirmed = _confirm(tmp_path, "Add collectible")
    increment_id = confirmed["facts"]["increment_id"]
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")
    reviewed = review_increment(tmp_path, increment_id)

    assert reviewed["facts"]["plan"] is not None
    (tmp_path / "scripts/game.js").write_text("export const score = 2;", encoding="utf-8")
    inspected = inspect_project(tmp_path)

    assert inspected["status"] == "review_required"
    assert inspected["facts"]["review_state"]["status"] == "review_required"


def test_review_flags_an_increment_that_has_remained_open_too_long(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    confirmed = _confirm(tmp_path, "Add collectible")
    state_path = tmp_path / ".gamemakergraph/review-state.json"
    state = json.loads(state_path.read_text("utf-8"))
    state["status_since"] = 0
    state_path.write_text(json.dumps(state), encoding="utf-8")
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")

    reviewed = review_increment(tmp_path, confirmed["facts"]["increment_id"])

    assert any(item["type"] == "review_overdue" for item in reviewed["facts"]["findings"])


def test_inspect_proactively_reports_offline_changes(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    _confirm(tmp_path, "Add collectible")
    (tmp_path / "scripts/game.js").write_text("export const score = 4;", encoding="utf-8")

    inspected = inspect_project(tmp_path)

    assert inspected["status"] == "review_required"
    assert inspected["facts"]["changed_paths"]["modified"] == ["scripts/game.js"]
    assert inspected["next_actions"] == [
        "Call gamegraph_review_increment for the active confirmed increment."
    ]


def test_inspect_recovers_confirmed_intent_when_disposable_state_was_deleted(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)
    confirmed = _confirm(tmp_path, "Add collectible")
    (tmp_path / ".gamemakergraph/review-state.json").unlink()
    (tmp_path / "scripts/game.js").write_text("export const score = 5;", encoding="utf-8")

    inspected = inspect_project(tmp_path)
    reviewed = review_increment(tmp_path, confirmed["facts"]["increment_id"])

    assert inspected["status"] == "review_required"
    assert inspected["facts"]["active_increment"]["goal"] == "Add collectible"
    assert any("baseline" in warning.lower() for warning in inspected["warnings"])
    assert any(item["type"] == "baseline_recovered" for item in reviewed["facts"]["findings"])


def test_review_rejects_an_unconfirmed_increment(tmp_path: Path) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)

    result = review_increment(tmp_path, "increment:missing")

    assert result["status"] == "not_found"
    assert result["facts"]["plan"] is None


def test_three_window_handoff_recovers_reviews_and_closes_the_increment(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    rebuild_graph(tmp_path)

    # Window A: confirm intent before implementation, then lose conversation context.
    prepared = prepare_increment(tmp_path, "Collect a star and increase score")
    confirmed = confirm_increment(
        tmp_path, prepared["revision"], prepared["facts"]["draft"]
    )
    increment_id = confirmed["facts"]["increment_id"]

    # Window B: implementation happens while no GameMakerGraph process is running.
    (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")

    # Window C: inspect discovers the offline change and resumes only from project state.
    resumed = inspect_project(tmp_path)
    assert resumed["status"] == "review_required"
    assert resumed["facts"]["active_increment"]["increment_id"] == increment_id
    reviewed = review_increment(
        tmp_path,
        increment_id,
        evidence=[
            {
                "kind": "user_confirmation",
                "claim": "User confirmed collecting the star increases score",
                "result": "passed",
                "revision": resumed["revision"],
            }
        ],
    )
    ready_to_apply = inspect_project(tmp_path)
    assert ready_to_apply["status"] == "maintenance_required"
    assert (
        ready_to_apply["facts"]["pending_plan"]["plan_id"]
        == reviewed["facts"]["plan"]["plan_id"]
    )
    applied = apply_maintenance(tmp_path, reviewed["revision"], reviewed["facts"]["plan"])
    closed = inspect_project(tmp_path)

    assert reviewed["facts"]["review_outcome"] == "validated"
    assert applied["status"] == "applied"
    assert closed["status"] == "ready"
    assert closed["facts"]["active_increment"] is None
    assert closed["facts"]["review_state"]["status"] == "documented/current"
    assert closed["facts"]["gamegraph"]["status"] == "current"


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
