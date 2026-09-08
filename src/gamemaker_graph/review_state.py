"""Disposable active-increment state and lightweight project monitoring."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Mapping

from .graph import (
    GRAPH_PATH,
    project_manifest,
    project_revision,
    project_signature,
    rebuild_graph,
)

REVIEW_STATE_PATH = Path(".gamemakergraph/review-state.json")
_STATE_LOCK = threading.RLock()


def _changes(before: Mapping[str, str], after: Mapping[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(after.keys() - before.keys()),
        "modified": sorted(
            path for path in before.keys() & after.keys() if before[path] != after[path]
        ),
        "removed": sorted(before.keys() - after.keys()),
    }


def _has_changes(changes: Mapping[str, list[str]]) -> bool:
    return any(changes.get(category) for category in ("added", "modified", "removed"))


def read_review_state(project_root: str | Path) -> dict[str, Any] | None:
    """Read the disposable review state without exposing malformed content."""

    root = Path(project_root).resolve()
    with _STATE_LOCK:
        try:
            value = json.loads((root / REVIEW_STATE_PATH).read_text("utf-8"))
        except (OSError, ValueError):
            return None
    return value if isinstance(value, dict) else None


def _write_review_state(root: Path, state: Mapping[str, Any]) -> None:
    rendered = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    target = root / REVIEW_STATE_PATH
    with _STATE_LOCK:
        try:
            if target.read_text("utf-8") == rendered:
                return
        except OSError:
            pass
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(rendered, "utf-8")
        temporary.replace(target)


def create_review_state(project_root: str | Path, draft: Mapping[str, Any]) -> dict[str, Any]:
    """Persist a baseline after an increment has been confirmed in Markdown."""

    root = Path(project_root).resolve()
    manifest = project_manifest(root)
    revision = project_revision(root)
    state: dict[str, Any] = {
        "schema_version": "0.6",
        "status": "confirmed",
        "active_increment": dict(draft),
        "baseline_revision": revision,
        "baseline_manifest": manifest,
        "observed_revision": revision,
        "changes": {"added": [], "modified": [], "removed": []},
        "evidence_gaps": list(draft.get("acceptance_criteria", [])),
        "pending_plan": None,
        "status_since": time.time(),
    }
    _write_review_state(root, state)
    return state


def recover_review_state(project_root: str | Path, draft: Mapping[str, Any]) -> dict[str, Any]:
    """Recover confirmed intent while making the missing historical baseline explicit."""

    root = Path(project_root).resolve()
    state = create_review_state(root, draft)
    state["status"] = "review_required"
    state["baseline_recovered"] = True
    state["pending_plan"] = None
    _write_review_state(root, state)
    return state


def reconcile_project(project_root: str | Path) -> dict[str, Any] | None:
    """Synchronously detect changes, refresh the graph, and persist Review need."""

    root = Path(project_root).resolve()
    state = read_review_state(root)
    if state is None:
        return None
    manifest = project_manifest(root)
    revision = project_revision(root)
    baseline = state.get("baseline_manifest")
    if not isinstance(baseline, dict):
        baseline = manifest
    changes = _changes(baseline, manifest)
    active = state.get("active_increment")
    if active and _has_changes(changes):
        review_is_current = (
            state.get("reviewed_revision") == revision
            and state.get("status") in {"implemented_unverified", "validated"}
        )
        if not review_is_current:
            state["status"] = "review_required"
            state["pending_plan"] = None
        state["changes"] = changes
    elif active and state.get("status") not in {"blocked", "rejected", "superseded"}:
        state["status"] = "confirmed"
        state["changes"] = changes
    state["observed_revision"] = revision

    graph = root / GRAPH_PATH
    rebuilt = rebuild_graph(root)
    if not graph.is_file() or rebuilt["changed"]:
        revision = project_revision(root)
        state["observed_revision"] = revision
    _write_review_state(root, state)
    return state


def record_review_result(
    project_root: str | Path,
    increment_id: str,
    *,
    outcome: str,
    evidence_gaps: list[str],
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Persist a derived Review result without changing semantic Markdown."""

    root = Path(project_root).resolve()
    state = read_review_state(root)
    if state is None:
        raise FileNotFoundError(root / REVIEW_STATE_PATH)
    active = state.get("active_increment")
    if not isinstance(active, dict) or active.get("increment_id") != increment_id:
        raise ValueError("review result does not match the active increment")
    if state.get("status") != outcome:
        state["status_since"] = time.time()
    state["status"] = outcome
    state["reviewed_revision"] = project_revision(root)
    state["evidence_gaps"] = list(evidence_gaps)
    state["pending_plan"] = dict(plan)
    _write_review_state(root, state)
    return state


def close_review_state(
    project_root: str | Path, increment_id: str, *, status: str = "documented/current"
) -> dict[str, Any]:
    """Close the matching active increment after confirmed maintenance is applied."""

    root = Path(project_root).resolve()
    state = read_review_state(root) or {}
    active = state.get("active_increment")
    if not isinstance(active, dict) or active.get("increment_id") != increment_id:
        return state
    rebuild_graph(root)
    revision = project_revision(root)
    state.update(
        {
            "schema_version": "0.6",
            "status": status,
            "active_increment": None,
            "last_increment_id": increment_id,
            "baseline_revision": revision,
            "baseline_manifest": project_manifest(root),
            "observed_revision": revision,
            "changes": {"added": [], "modified": [], "removed": []},
            "evidence_gaps": [],
            "pending_plan": None,
            "status_since": time.time(),
        }
    )
    _write_review_state(root, state)
    return state


class ReviewMonitor:
    """Poll registered roots and reconcile them after a short debounce."""

    def __init__(self, *, poll_interval: float = 0.25, debounce_seconds: float = 1.0) -> None:
        self.poll_interval = poll_interval
        self.debounce_seconds = debounce_seconds
        self._roots: dict[Path, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def register(self, project_root: str | Path) -> dict[str, Any] | None:
        root = Path(project_root).resolve()
        state = reconcile_project(root)
        with self._lock:
            self._roots[root] = {
                "signature": project_signature(root),
                "changed_at": None,
            }
        return state

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._run, name="gamemakergraph-review-monitor", daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.wait(self.poll_interval):
            with self._lock:
                roots = list(self._roots.items())
            now = time.monotonic()
            for root, tracked in roots:
                try:
                    signature = project_signature(root)
                except (OSError, NotADirectoryError):
                    continue
                if signature == tracked["signature"]:
                    tracked["changed_at"] = None
                    continue
                if tracked["changed_at"] is None:
                    tracked["changed_at"] = now
                    continue
                if now - tracked["changed_at"] < self.debounce_seconds:
                    continue
                try:
                    reconcile_project(root)
                    tracked["signature"] = project_signature(root)
                    tracked["changed_at"] = None
                except (OSError, ValueError):
                    continue
