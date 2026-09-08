import time
from pathlib import Path

from gamemaker_graph.graph import graph_status, rebuild_graph
from gamemaker_graph.review_state import ReviewMonitor, read_review_state
from gamemaker_graph.workflow import confirm_increment, prepare_increment


def _project(root: Path) -> None:
    (root / "scripts").mkdir()
    (root / "scripts/game.js").write_text("export const score = 0;", encoding="utf-8")
    memory = root / "docs/development/project-memory.md"
    memory.parent.mkdir(parents=True)
    memory.write_text(
        "# Project Memory\n\n<!-- GAMEGRAPH:START -->\n```json\n"
        '{"nodes": [], "edges": [], "applied_plans": []}\n'
        "```\n<!-- GAMEGRAPH:END -->\n",
        encoding="utf-8",
    )


def _confirmed(root: Path) -> str:
    rebuild_graph(root)
    prepared = prepare_increment(root, "Collect a star")
    result = confirm_increment(root, prepared["revision"], prepared["facts"]["draft"])
    return result["facts"]["increment_id"]


def test_monitor_marks_changed_project_for_review_and_keeps_graph_current(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    _confirmed(tmp_path)
    monitor = ReviewMonitor(poll_interval=0.02, debounce_seconds=0.04)
    monitor.register(tmp_path)
    monitor.start()
    try:
        (tmp_path / "scripts/game.js").write_text("export const score = 1;", encoding="utf-8")
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            state = read_review_state(tmp_path)
            if state and state["status"] == "review_required":
                break
            time.sleep(0.02)
        else:
            raise AssertionError("monitor did not request review")
    finally:
        monitor.stop()

    assert state["changes"]["modified"] == ["scripts/game.js"]
    assert graph_status(tmp_path)["status"] == "current"


def test_monitor_debounces_fast_changes_and_handles_multiple_projects(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    _project(first)
    _project(second)
    _confirmed(first)
    _confirmed(second)
    monitor = ReviewMonitor(poll_interval=0.02, debounce_seconds=0.05)
    monitor.register(first)
    monitor.register(second)
    monitor.start()
    try:
        for value in range(3):
            (first / "scripts/game.js").write_text(
                f"export const score = {value + 1};", encoding="utf-8"
            )
        (second / "scripts/game.js").unlink()
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            first_state = read_review_state(first)
            second_state = read_review_state(second)
            if (
                first_state
                and second_state
                and first_state["status"] == "review_required"
                and second_state["status"] == "review_required"
            ):
                break
            time.sleep(0.02)
        else:
            raise AssertionError("monitor did not reconcile both projects")
    finally:
        monitor.stop()

    assert first_state["changes"]["modified"] == ["scripts/game.js"]
    assert second_state["changes"]["removed"] == ["scripts/game.js"]
