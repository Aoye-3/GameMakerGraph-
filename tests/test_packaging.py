import json
import tomllib
from pathlib import Path

import gamemaker_graph


def test_package_and_runtime_versions_match_the_current_contract() -> None:
    metadata = tomllib.loads(Path("pyproject.toml").read_text("utf-8"))

    assert metadata["project"]["version"] == gamemaker_graph.__version__ == "0.5.0"
    assert metadata["project"]["optional-dependencies"]["mcp"] == ["mcp>=2,<3"]
    assert metadata["project"]["scripts"]["gamegraph-mcp"] == "gamemaker_graph.mcp_server:main"


def test_plugin_manifest_exposes_the_complete_skill_set() -> None:
    plugin_root = Path(".")
    manifest = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text("utf-8"))
    expected = {
        "codegraph-documentation",
        "game-art-direction",
        "game-direction",
        "game-project-bootstrap",
        "game-project-exploration",
        "game-quality-review",
        "minigame-validation",
    }

    assert manifest["name"] == "gamemaker-graph"
    assert manifest["version"] == "0.5.0"
    assert manifest["mcpServers"] == "./.mcp.json"

    mcp_config = json.loads(Path(".mcp.json").read_text("utf-8"))
    assert mcp_config["mcpServers"]["gamemaker-graph"]["command"] == "gamegraph-mcp"
    assert manifest["skills"] == "./skills/"
    assert {path.name for path in (plugin_root / "skills").iterdir() if path.is_dir()} == expected
    for name in expected:
        skill_root = plugin_root / "skills" / name
        assert (skill_root / "SKILL.md").is_file()
        assert (skill_root / "agents/openai.yaml").is_file()
