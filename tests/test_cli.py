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
