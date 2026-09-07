import json
from pathlib import Path

from gamemaker_graph.cli import main


def test_cli_build_and_search_emit_machine_readable_json(tmp_path: Path, capsys: object) -> None:
    (tmp_path / "design.md").write_text("# Movement\n\nDash and jump.\n", "utf-8")

    assert main(["build", str(tmp_path)]) == 0
    build_output = json.loads(capsys.readouterr().out)
    assert build_output["status"] == "current"

    assert main(["search", "dash", str(tmp_path)]) == 0
    search_output = json.loads(capsys.readouterr().out)
    assert search_output["results"][0]["source"] == "design.md"


def test_cli_context_and_impact_can_run_without_codegraph(tmp_path: Path, capsys: object) -> None:
    (tmp_path / "design.md").write_text("# Movement\n\nDash and jump.\n", "utf-8")
    main(["build", str(tmp_path)])
    capsys.readouterr()

    assert main(["context", "movement", str(tmp_path), "--no-codegraph"]) == 0
    context = json.loads(capsys.readouterr().out)
    assert context["nodes"][0]["source"] == "design.md"

    assert main(["impact", "file:design.md", str(tmp_path), "--no-codegraph"]) == 0
    impact = json.loads(capsys.readouterr().out)
    assert impact["root"] == "file:design.md"


def test_cli_docs_init_and_check_emit_machine_readable_json(tmp_path: Path, capsys: object) -> None:
    assert main(["docs", "init", str(tmp_path)]) == 0
    initialized = json.loads(capsys.readouterr().out)
    assert "docs/README.md" in initialized["created"]

    assert main(["docs", "check", str(tmp_path)]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["operation"] == "check"


def test_cli_trial_status_and_plan_emit_machine_readable_json(
    tmp_path: Path, capsys: object
) -> None:
    assert main(["trial", "status", str(tmp_path)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "blocked"

    assert main(["trial", "plan", str(tmp_path)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["operation"] == "plan"
    assert plan["provider"] == "taptap-maker"
