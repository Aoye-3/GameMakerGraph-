"""Continuous-memory workflow shared by the CLI and MCP adapter."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .codegraph import CodeGraphProvider
from .docs import inspect_docs
from .graph import (
    GRAPH_PATH,
    _read_graph,
    build_graph,
    graph_status,
    project_revision,
    rebuild_graph,
)
from .semantic import (
    END_MARKER,
    SEMANTIC_EDGE_KINDS,
    SEMANTIC_NODE_KINDS,
    START_MARKER,
    relationship_allowed,
)

SCHEMA_VERSION = "0.5"
PROJECT_MEMORY = "docs/development/project-memory.md"
_CONTROLLED = re.compile(
    rf"(?P<start>^{re.escape(START_MARKER)}\s*$\n?)(?P<body>.*?)(?P<end>^\s*{re.escape(END_MARKER)}\s*$)",
    re.MULTILINE | re.DOTALL,
)


def _root(project_root: str | Path) -> Path:
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    return root


def _envelope(
    operation: str,
    root: Path,
    status: str,
    *,
    revision: str | None = None,
    facts: Mapping[str, Any] | None = None,
    warnings: Sequence[str] = (),
    next_actions: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "status": status,
        "project_root": str(root),
        "revision": revision if revision is not None else project_revision(root),
        "facts": dict(facts or {}),
        "warnings": sorted(set(warnings)),
        "next_actions": list(next_actions),
    }


def error_envelope(operation: str, project_root: object, exc: Exception) -> dict[str, Any]:
    """Return the public error shape without echoing unsafe input contents."""

    try:
        displayed_root = str(Path(str(project_root)).resolve())
    except (OSError, TypeError, ValueError):
        displayed_root = "<invalid>"
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "status": "error",
        "project_root": displayed_root,
        "revision": None,
        "facts": {"error_type": type(exc).__name__},
        "warnings": [str(exc)],
        "next_actions": ["Correct the input and retry the same operation."],
    }


def _public_node(node: Mapping[str, Any]) -> dict[str, Any]:
    details = dict(node.get("details", {}))
    details.pop("search_text", None)
    return {
        "id": node["id"],
        "kind": node["kind"],
        "label": node["label"],
        "source": node["source"],
        "details": details,
    }


def _local_matches(graph: Mapping[str, Any], query: str, limit: int = 20) -> list[dict[str, Any]]:
    terms = [term.casefold() for term in query.split() if term.strip()]
    matches: list[tuple[int, Mapping[str, Any]]] = []
    for node in graph["nodes"]:
        identity = f"{node['label']} {node['source']}".casefold()
        details = json.dumps(node.get("details", {}), ensure_ascii=False).casefold()
        if terms and all(term in identity or term in details for term in terms):
            score = sum(2 if term in identity else 1 for term in terms)
            matches.append((score, node))
    matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [_public_node(item[1]) for item in matches[:limit]]


def inspect_project(project_root: str | Path) -> dict[str, Any]:
    """Inspect project memory, documentation, graph freshness, and optional providers."""

    root = _root(project_root)
    state = graph_status(root)
    provider = CodeGraphProvider.auto().status(root)
    return _envelope(
        "gamegraph_inspect_project",
        root,
        "ready" if state["status"] == "current" else state["status"],
        facts={
            "gamegraph": state,
            "documentation": inspect_docs(root),
            "codegraph": provider,
            "maker": {
                "configured": (root / ".maker-mcp/config.json").is_file(),
                "config_content_read": False,
            },
        },
        warnings=[] if state["status"] == "current" else [f"GameGraph is {state['status']}."],
        next_actions=(
            ["Call gamegraph_prepare_increment before the next code change."]
            if state["status"] == "current"
            else ["Call gamegraph_rebuild_index before relying on indexed relationships."]
        ),
    )


def prepare_increment(project_root: str | Path, goal: str) -> dict[str, Any]:
    """Prepare source-backed context and confirmation candidates without writing files."""

    root = _root(project_root)
    goal = goal.strip()
    if not goal:
        raise ValueError("goal must not be empty")
    state = graph_status(root)
    graph = _read_graph(root) if state["status"] == "current" else build_graph(root)
    assert graph is not None
    matches = _local_matches(graph, goal)
    provider = CodeGraphProvider.auto().context(root, goal, limit=10)
    warnings = list(graph.get("warnings", []))
    if state["status"] != "current":
        warnings.append(
            f"GameGraph is {state['status']}; local facts were derived in memory and not persisted."
        )
    return _envelope(
        "gamegraph_prepare_increment",
        root,
        "ready" if state["status"] == "current" else "index_required",
        facts={
            "goal": goal,
            "local_context": matches,
            "code_context": provider,
            "questions": [
                "请确认这次增量只包含一个可观察的玩家或系统变化。",
                "请确认验收必须来自同一版本的实际运行或试玩，而不只是构建成功。",
            ],
            "acceptance_candidates": [
                {
                    "kind": "acceptance_criterion",
                    "claim": f"在真实运行中可以观察到目标产生的状态变化：{goal}",
                    "confirmation_required": True,
                }
            ],
            "candidate_persistence": "none",
        },
        warnings=warnings,
        next_actions=[
            "Ask the user to confirm scope and observable acceptance before implementation.",
            "Use the separate engine or Maker MCP to implement and run the confirmed increment.",
        ],
    )


def query_project(
    project_root: str | Path, query: str, include_code: bool = True
) -> dict[str, Any]:
    """Query current semantic/project facts and optionally CodeGraph."""

    root = _root(project_root)
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    state = graph_status(root)
    graph = _read_graph(root) if state["status"] == "current" else build_graph(root)
    assert graph is not None
    code = (
        CodeGraphProvider.auto().context(root, query, limit=20)
        if include_code
        else {"provider": "codegraph", "status": "disabled", "symbols": []}
    )
    warnings = list(graph.get("warnings", []))
    if state["status"] != "current":
        warnings.append(
            f"Persisted GameGraph is {state['status']}; rebuild it for a current index."
        )
    return _envelope(
        "gamegraph_query",
        root,
        "current" if state["status"] == "current" else state["status"],
        facts={"query": query, "matches": _local_matches(graph, query), "codegraph": code},
        warnings=warnings,
        next_actions=(
            []
            if state["status"] == "current"
            else ["Call gamegraph_rebuild_index before using graph relationships for decisions."]
        ),
    )


def _relative_path(root: Path, value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        return None
    resolved = (root / Path(*path.parts)).resolve()
    return path.as_posix() if resolved.is_relative_to(root) else None


def _artifact_hashes(graph: Mapping[str, Any] | None) -> dict[str, str]:
    if graph is None:
        return {}
    return {
        node["source"]: node["details"]["sha256"]
        for node in graph.get("nodes", [])
        if node.get("id", "").startswith("file:") and "sha256" in node.get("details", {})
    }


def _changes(before: Mapping[str, str], after: Mapping[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(after.keys() - before.keys()),
        "modified": sorted(
            path for path in before.keys() & after.keys() if before[path] != after[path]
        ),
        "removed": sorted(before.keys() - after.keys()),
    }


def _goal_key(goal: str) -> str:
    return hashlib.sha256(goal.strip().casefold().encode()).hexdigest()[:12]


def _sanitize_evidence(
    root: Path, evidence: Sequence[Mapping[str, Any]], warnings: list[str]
) -> list[dict[str, Any]]:
    clean: list[dict[str, Any]] = []
    allowed = {"path", "kind", "claim", "result", "observed_at", "tool"}
    for index, raw in enumerate(evidence):
        item = {key: raw[key] for key in allowed if key in raw}
        if "path" in item:
            relative = _relative_path(root, item["path"])
            if relative is None:
                warnings.append(f"Dropped evidence item {index}: path must be project-relative.")
                continue
            item["path"] = relative
            if not (root / relative).is_file():
                warnings.append(f"Evidence path does not exist yet: {relative}")
        if not item.get("claim"):
            warnings.append(f"Dropped evidence item {index}: claim is required.")
            continue
        clean.append(item)
    return clean


def _plan_id(plan: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in plan.items() if key != "plan_id"}
    canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "plan:" + hashlib.sha256(canonical.encode()).hexdigest()


def review_increment(
    project_root: str | Path,
    goal: str,
    base_revision: str,
    evidence: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Review an increment and return a deterministic maintenance preview without writing."""

    root = _root(project_root)
    goal = goal.strip()
    if not goal:
        raise ValueError("goal must not be empty")
    indexed = _read_graph(root)
    if indexed is None or indexed.get("revision") != base_revision:
        return _envelope(
            "gamegraph_review_increment",
            root,
            "conflict",
            facts={"base_revision": base_revision, "plan": None},
            warnings=["The requested base revision is not the persisted GameGraph baseline."],
            next_actions=["Rebuild the index, prepare the increment again, and retry review."],
        )

    current = build_graph(root)
    changed = _changes(_artifact_hashes(indexed), _artifact_hashes(current))
    warnings: list[str] = list(current.get("warnings", []))
    clean_evidence = _sanitize_evidence(root, evidence, warnings)
    if not clean_evidence:
        warnings.append("No accepted runtime or playtest evidence was supplied.")

    digest = _goal_key(goal)
    feature_key = f"feature-{digest}"
    acceptance_key = f"acceptance-{digest}"
    nodes: list[dict[str, Any]] = [
        {"key": feature_key, "kind": "feature", "label": goal, "status": "implemented"},
        {
            "key": acceptance_key,
            "kind": "acceptance_criterion",
            "label": f"可观察验收：{goal}",
            "status": "needs_evidence" if not clean_evidence else "reviewed",
        },
    ]
    edges: list[dict[str, str]] = [
        {"source": feature_key, "target": PROJECT_MEMORY, "kind": "documents"},
        {"source": acceptance_key, "target": feature_key, "kind": "depends_on"},
    ]
    implementation_paths = [
        path
        for category in ("added", "modified")
        for path in changed[category]
        if not path.casefold().endswith(".md")
    ]
    edges.extend(
        {"source": feature_key, "target": path, "kind": "implemented_by"}
        for path in implementation_paths
    )
    for item in clean_evidence:
        evidence_digest = hashlib.sha256(
            json.dumps(item, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()[:12]
        key = f"evidence-{evidence_digest}"
        nodes.append(
            {
                "key": key,
                "kind": "validation_evidence",
                "label": str(item["claim"]),
                **{field: value for field, value in item.items() if field != "claim"},
            }
        )
        edges.append({"source": acceptance_key, "target": key, "kind": "validated_by"})

    plan: dict[str, Any] = {
        "goal": goal,
        "base_revision": base_revision,
        "review_revision": current["revision"],
        "document_changes": [
            {"path": PROJECT_MEMORY, "nodes": nodes, "edges": edges}
        ],
    }
    plan["plan_id"] = _plan_id(plan)
    return _envelope(
        "gamegraph_review_increment",
        root,
        "review_required",
        revision=current["revision"],
        facts={
            "goal": goal,
            "base_revision": base_revision,
            "changes": changed,
            "evidence": clean_evidence,
            "plan": plan,
        },
        warnings=warnings,
        next_actions=[
            "Review the maintenance preview with the user.",
            "After explicit confirmation, pass this exact plan to gamegraph_apply_maintenance.",
        ],
    )


def _empty_payload() -> dict[str, list[Any]]:
    return {"nodes": [], "edges": [], "applied_plans": []}


def _decode_controlled(text: str) -> tuple[re.Match[str] | None, dict[str, Any]]:
    match = _CONTROLLED.search(text)
    if match is None:
        return None, _empty_payload()
    body = match.group("body").strip()
    lines = body.splitlines()
    if lines and lines[0].strip().casefold() in {"```", "```json"}:
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ValueError("project memory has an invalid GAMEGRAPH fence")
        body = "\n".join(lines[1:-1])
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("project memory GAMEGRAPH payload must be an object")
    for field in ("nodes", "edges", "applied_plans"):
        if not isinstance(payload.get(field, []), list):
            raise ValueError(f"project memory GAMEGRAPH {field} must be an array")
        payload.setdefault(field, [])
    return match, payload


def _validate_plan(root: Path, plan: Mapping[str, Any]) -> dict[str, Any]:
    if plan.get("plan_id") != _plan_id(plan):
        raise ValueError("plan_id does not match the deterministic plan content")
    changes = plan.get("document_changes")
    if not isinstance(changes, list) or len(changes) != 1:
        raise ValueError("plan must contain exactly one closed-world document change")
    change = changes[0]
    if not isinstance(change, dict) or change.get("path") != PROJECT_MEMORY:
        raise ValueError(f"plan may only maintain {PROJECT_MEMORY}")
    raw_nodes = change.get("nodes", [])
    raw_edges = change.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("plan nodes and edges must be arrays")
    node_kinds: dict[str, str] = {}
    for node in raw_nodes:
        if (
            not isinstance(node, dict)
            or node.get("kind") not in SEMANTIC_NODE_KINDS
            or not isinstance(node.get("key"), str)
            or not isinstance(node.get("label"), str)
        ):
            raise ValueError("plan contains an invalid semantic node")
        if "path" in node and _relative_path(root, node["path"]) is None:
            raise ValueError("plan contains a non-relative evidence path")
        key = node["key"].strip().casefold()
        if key in node_kinds:
            raise ValueError("plan contains duplicate semantic keys")
        node_kinds[key] = node["kind"]
    for edge in raw_edges:
        if (
            not isinstance(edge, dict)
            or edge.get("kind") not in SEMANTIC_EDGE_KINDS
            or not isinstance(edge.get("source"), str)
            or not isinstance(edge.get("target"), str)
        ):
            raise ValueError("plan contains an invalid semantic edge")
        source_kind = node_kinds.get(edge["source"].strip().casefold())
        target_kind = node_kinds.get(edge["target"].strip().casefold())
        target_path = None if target_kind else _relative_path(root, edge["target"])
        target_is_file = (
            target_kind is None
            and target_path is not None
            and (root / target_path).is_file()
        )
        if edge["kind"] == "documents" and (
            target_path is None or not target_path.casefold().endswith(".md")
        ):
            target_is_file = False
        if source_kind is None or not relationship_allowed(
            source_kind,
            target_kind,
            edge["kind"],
            target_is_file=target_is_file,
        ):
            raise ValueError("plan contains an invalid semantic relationship")
    return change


def _render_payload(payload: Mapping[str, Any]) -> str:
    return "```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```\n"


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def apply_maintenance(
    project_root: str | Path, expected_revision: str, plan: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply one confirmed closed-world document plan, preserving all human text."""

    root = _root(project_root)
    change = _validate_plan(root, plan)
    if plan.get("review_revision") != expected_revision:
        raise ValueError("expected_revision must match the plan review_revision")
    plan_id = str(plan["plan_id"])
    target = root / PROJECT_MEMORY
    text = (
        target.read_text("utf-8-sig", errors="strict")
        if target.is_file()
        else "# Project Memory\n"
    )
    match, payload = _decode_controlled(text)

    if plan_id in payload["applied_plans"]:
        return _envelope(
            "gamegraph_apply_maintenance",
            root,
            "unchanged",
            facts={"plan_id": plan_id, "changed_paths": []},
            next_actions=["Call gamegraph_rebuild_index if the graph is stale."],
        )
    live_revision = project_revision(root)
    if expected_revision != live_revision:
        return _envelope(
            "gamegraph_apply_maintenance",
            root,
            "conflict",
            facts={"plan_id": plan_id, "expected_revision": expected_revision},
            warnings=["Project revision changed after review; no document was modified."],
            next_actions=["Run gamegraph_review_increment again against the latest project state."],
        )

    by_key = {node.get("key"): node for node in payload["nodes"] if isinstance(node, dict)}
    for node in change.get("nodes", []):
        by_key[node["key"]] = node
    payload["nodes"] = sorted(by_key.values(), key=lambda item: (item["kind"], item["key"]))
    edge_keys = {
        (edge.get("source"), edge.get("target"), edge.get("kind")): edge
        for edge in payload["edges"]
        if isinstance(edge, dict)
    }
    for edge in change.get("edges", []):
        edge_keys[(edge["source"], edge["target"], edge["kind"])] = edge
    payload["edges"] = sorted(
        edge_keys.values(), key=lambda item: (item["source"], item["target"], item["kind"])
    )
    payload["applied_plans"] = sorted({*payload["applied_plans"], plan_id})
    body = _render_payload(payload)
    if match is None:
        separator = "" if text.endswith("\n\n") else "\n" if text.endswith("\n") else "\n\n"
        updated = text + separator + START_MARKER + "\n" + body + END_MARKER + "\n"
    else:
        updated = text[: match.start("body")] + body + text[match.end("body") :]
    _write_text_atomic(target, updated)
    return _envelope(
        "gamegraph_apply_maintenance",
        root,
        "applied",
        facts={"plan_id": plan_id, "changed_paths": [PROJECT_MEMORY]},
        next_actions=["Call gamegraph_rebuild_index to make the derived graph current."],
    )


def rebuild_index(project_root: str | Path) -> dict[str, Any]:
    """Idempotently rebuild the derived GameGraph index from project sources."""

    root = _root(project_root)
    result = rebuild_graph(root)
    return _envelope(
        "gamegraph_rebuild_index",
        root,
        "current",
        revision=result["revision"],
        facts={
            "index": GRAPH_PATH.as_posix(),
            "changed": result["changed"],
            "nodes": result["nodes"],
            "edges": result["edges"],
        },
        warnings=[] if not result["warnings"] else [f"Index has {result['warnings']} warning(s)."],
        next_actions=["Call gamegraph_prepare_increment for the next confirmed increment."],
    )
