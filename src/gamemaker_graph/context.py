"""Bounded gameplay context and impact queries over a current GameGraph."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Mapping

from .codegraph import CodeGraphProvider
from .graph import _require_graph


def _public_node(node: Mapping[str, Any], distance: int) -> dict[str, Any]:
    details = dict(node.get("details", {}))
    details.pop("search_text", None)
    return {
        "id": node["id"],
        "kind": node["kind"],
        "label": node["label"],
        "source": node["source"],
        "distance": distance,
        "details": details,
    }


def _semantic_neighborhood(
    graph: Mapping[str, Any], seeds: list[str], *, depth: int, limit: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {node["id"]: node for node in graph["nodes"]}
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    semantic_edges = [edge for edge in graph["edges"] if edge["kind"] != "contains"]
    for edge in semantic_edges:
        adjacency[edge["source"]].append(edge["target"])
        adjacency[edge["target"]].append(edge["source"])

    distance = {seed: 0 for seed in seeds if seed in by_id}
    queue = deque(sorted(distance))
    while queue:
        current = queue.popleft()
        if distance[current] >= depth:
            continue
        for neighbor in sorted(adjacency[current]):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    ordered_ids = sorted(distance, key=lambda node_id: (distance[node_id], node_id))[:limit]
    selected = set(ordered_ids)
    nodes = [_public_node(by_id[node_id], distance[node_id]) for node_id in ordered_ids]
    edges = [
        edge for edge in semantic_edges if edge["source"] in selected and edge["target"] in selected
    ]
    return nodes, edges


def _blocked_result(
    graph: Mapping[str, Any], status: Mapping[str, Any], *, query: str | None = None
) -> dict[str, Any]:
    result = {
        "schema_version": "0.2",
        "status": status["status"],
        "blocked": True,
        "revision": graph.get("revision"),
        "nodes": [],
        "edges": [],
        "codegraph": {"provider": "codegraph", "status": "not_queried"},
    }
    if query is not None:
        result["query"] = query
    return result


def task_context(
    project_root: Path,
    query: str,
    *,
    depth: int = 2,
    limit: int = 20,
    include_code: bool = True,
    codegraph: CodeGraphProvider | None = None,
) -> dict[str, Any]:
    """Return a bounded project neighborhood plus optional CodeGraph symbols."""
    root, graph, status = _require_graph(project_root)
    if status["status"] != "current":
        return _blocked_result(graph, status, query=query)

    terms = [term.casefold() for term in query.split() if term.strip()]
    scored: list[tuple[int, str]] = []
    for node in graph["nodes"]:
        identity = f"{node['label']} {node['source']}".casefold()
        details = json.dumps(node.get("details", {}), ensure_ascii=False).casefold()
        if terms and all(term in identity or term in details for term in terms):
            score = sum(2 if term in identity else 1 for term in terms)
            scored.append((score, node["id"]))
    scored.sort(key=lambda item: (-item[0], item[1]))

    depth = max(0, min(depth, 3))
    limit = max(1, min(limit, 100))
    seeds = [node_id for _, node_id in scored[: min(limit, 10)]]
    nodes, edges = _semantic_neighborhood(graph, seeds, depth=depth, limit=limit)
    code_context = (
        (codegraph or CodeGraphProvider.auto()).context(root, query, limit=min(limit, 20))
        if include_code
        else {"provider": "codegraph", "status": "disabled", "symbols": []}
    )
    return {
        "schema_version": "0.2",
        "status": "current",
        "blocked": False,
        "query": query,
        "revision": graph["revision"],
        "seed_ids": seeds,
        "nodes": nodes,
        "edges": edges,
        "codegraph": code_context,
    }


def impact_graph(
    project_root: Path,
    root_id: str,
    *,
    depth: int = 2,
    include_code: bool = True,
    code_symbol: str | None = None,
    codegraph: CodeGraphProvider | None = None,
) -> dict[str, Any]:
    """Return a bounded semantic blast radius with optional code-symbol impact."""
    root, graph, status = _require_graph(project_root)
    if status["status"] != "current":
        return _blocked_result(graph, status)
    if root_id not in {node["id"] for node in graph["nodes"]}:
        raise KeyError(f"Unknown GameGraph node: {root_id}")

    depth = max(0, min(depth, 3))
    nodes, edges = _semantic_neighborhood(graph, [root_id], depth=depth, limit=100)
    if not include_code:
        code_impact = {"provider": "codegraph", "status": "disabled", "affected": []}
    elif code_symbol is None:
        code_impact = {"provider": "codegraph", "status": "not_requested", "affected": []}
    else:
        code_impact = (codegraph or CodeGraphProvider.auto()).impact(
            root, code_symbol, depth=max(1, depth)
        )
    return {
        "schema_version": "0.2",
        "status": "current",
        "blocked": False,
        "root": root_id,
        "depth": depth,
        "revision": graph["revision"],
        "nodes": nodes,
        "edges": edges,
        "codegraph": code_impact,
    }
