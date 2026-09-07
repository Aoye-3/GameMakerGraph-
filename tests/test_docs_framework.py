from pathlib import Path

from gamemaker_graph.docs import check_docs, init_docs, inspect_docs, suggest_docs

BASE_DOCUMENTS = {
    "docs/README.md",
    "docs/product/overview.md",
    "docs/architecture/overview.md",
    "docs/architecture/implementation-map.md",
    "docs/development/setup.md",
    "docs/development/testing.md",
}


def test_suggest_returns_a_minimal_set_for_a_generic_project(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/main.py").write_text("print('hello')\n", "utf-8")

    result = suggest_docs(tmp_path)

    assert result["project_capabilities"] == []
    assert {item["path"] for item in result["suggestions"]} == BASE_DOCUMENTS
    assert all(item["state"] == "missing" for item in result["suggestions"])
    assert not (tmp_path / "docs").exists()


def test_suggest_adds_only_documents_supported_by_project_evidence(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n", "utf-8")
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"latest"}}', "utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "backend").mkdir()
    (tmp_path / "Dockerfile").write_text("FROM scratch\n", "utf-8")

    result = suggest_docs(tmp_path)
    paths = {item["path"] for item in result["suggestions"]}

    assert result["project_capabilities"] == ["game", "frontend", "backend", "delivery"]
    assert "docs/product/gameplay.md" in paths
    assert "docs/architecture/frontend.md" in paths
    assert "docs/architecture/backend.md" in paths
    assert "docs/delivery/release.md" in paths


def test_frontend_assets_directory_alone_does_not_imply_a_game_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"latest"}}', "utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "assets").mkdir()

    result = suggest_docs(tmp_path)

    assert result["project_capabilities"] == ["frontend"]
    assert "docs/product/gameplay.md" not in {item["path"] for item in result["suggestions"]}


def test_taptap_maker_binding_is_game_project_evidence(tmp_path: Path) -> None:
    binding = tmp_path / ".maker-mcp/config.json"
    binding.parent.mkdir(parents=True)
    binding.write_text("{}\n", "utf-8")

    result = suggest_docs(tmp_path)

    assert result["project_capabilities"] == ["game"]
    assert "docs/product/gameplay.md" in {item["path"] for item in result["suggestions"]}


def test_inspect_is_read_only_and_reports_gamegraph_state(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Existing\n", "utf-8")
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}

    result = inspect_docs(tmp_path)

    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    assert before == after
    assert result["gamegraph"]["status"] == "missing"
    assert result["documents"][0]["path"] == "README.md"


def test_init_creates_missing_documents_and_never_overwrites_existing_content(
    tmp_path: Path,
) -> None:
    existing = tmp_path / "docs/product/overview.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Confirmed Project Direction\n", "utf-8")
    original_mtime = existing.stat().st_mtime_ns

    first = init_docs(tmp_path)
    second = init_docs(tmp_path)

    assert existing.read_text("utf-8") == "# Confirmed Project Direction\n"
    assert existing.stat().st_mtime_ns == original_mtime
    assert "docs/product/overview.md" in first["preserved"]
    assert set(first["created"]) == BASE_DOCUMENTS - {"docs/product/overview.md"}
    assert second["created"] == []
    assert set(second["preserved"]) == BASE_DOCUMENTS
    generated = (tmp_path / "docs/architecture/implementation-map.md").read_text("utf-8")
    assert "## To confirm" in generated
    assert "## Implementation map" in generated


def test_check_reports_missing_broken_links_and_unconfirmed_template_items(
    tmp_path: Path,
) -> None:
    init_docs(tmp_path)
    (tmp_path / "docs/product/overview.md").write_text(
        "# Overview\n\nSee [missing](../architecture/missing.md).\n\n"
        "## To confirm\n\n- [ ] Audience\n",
        "utf-8",
    )
    (tmp_path / "docs/development/testing.md").unlink()

    result = check_docs(tmp_path)
    codes = {issue["code"] for issue in result["issues"]}

    assert result["status"] == "issues"
    assert "missing-document" in codes
    assert "broken-link" in codes
    assert "unconfirmed-items" in codes
    assert "empty-implementation-map" in codes
