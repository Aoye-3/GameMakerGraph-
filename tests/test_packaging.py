import tomllib
from pathlib import Path

import gamemaker_graph


def test_package_and_runtime_versions_match_the_current_contract() -> None:
    metadata = tomllib.loads(Path("pyproject.toml").read_text("utf-8"))

    assert metadata["project"]["version"] == gamemaker_graph.__version__ == "0.2.0"
