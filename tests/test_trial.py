from pathlib import Path

from gamemaker_graph.trial import prepare_trial, trial_plan, trial_status


def _maker_project(root: Path) -> None:
    config = root / ".maker-mcp/config.json"
    config.parent.mkdir(parents=True)
    config.write_text('{"secret":"must-not-be-read-or-returned"}\n', "utf-8")
    (root / "scripts").mkdir()
    (root / "scripts/main.lua").write_text("return {}\n", "utf-8")
    (root / "assets").mkdir()


def test_status_separates_project_readiness_from_live_mcp_connection(tmp_path: Path) -> None:
    _maker_project(tmp_path)

    result = trial_status(tmp_path)

    assert result["status"] == "preparation_required"
    assert result["checks"]["maker_project_bound"] is True
    assert result["checks"]["maker_structure_present"] is True
    assert result["provider_connection"] == "unverified"
    assert "secret" not in str(result)


def test_prepare_refuses_an_uninitialized_directory_without_writing(tmp_path: Path) -> None:
    before = list(tmp_path.rglob("*"))

    result = prepare_trial(tmp_path)

    assert result["status"] == "blocked"
    assert result["changed"] is False
    assert list(tmp_path.rglob("*")) == before


def test_uninitialized_status_does_not_suggest_preparing_the_wrong_directory(
    tmp_path: Path,
) -> None:
    result = trial_status(tmp_path)

    assert "<maker-project>" in result["next_actions"][1]
    assert str(tmp_path) not in result["next_actions"][1]


def test_prepare_builds_docs_then_a_current_gamegraph_for_a_maker_project(
    tmp_path: Path,
) -> None:
    _maker_project(tmp_path)

    result = prepare_trial(tmp_path)

    assert result["status"] == "ready_for_live_validation"
    assert result["changed"] is True
    assert (tmp_path / "docs/product/gameplay.md").is_file()
    assert (tmp_path / ".gamemakergraph/graph.json").is_file()
    assert result["gamegraph"]["status"] == "current"
    assert trial_status(tmp_path)["status"] == "ready_for_live_validation"


def test_plan_is_read_only_and_defines_observable_acceptance(tmp_path: Path) -> None:
    _maker_project(tmp_path)
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}

    result = trial_plan(tmp_path)

    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    acceptance_ids = {item["id"] for item in result["acceptance"]}
    assert before == after
    assert {"launch", "primary-verb", "goal", "restart", "diagnostics", "fresh-context"} <= (
        acceptance_ids
    )
    assert result["provider_connection"] == "unverified"
