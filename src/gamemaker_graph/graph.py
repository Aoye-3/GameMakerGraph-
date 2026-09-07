"""Build and query a disposable graph of a local game project."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from .semantic import parse_semantic_documents

INDEX_DIRECTORY = Path(".gamemakergraph")
GRAPH_PATH = INDEX_DIRECTORY / "graph.json"
IGNORED_DIRECTORIES = {
    ".gamemakergraph",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}
TEXT_SUFFIXES = {
    ".cfg",
    ".cs",
    ".gd",
    ".godot",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".tres",
    ".ts",
    ".tscn",
    ".txt",
    ".yaml",
    ".yml",
}
RESOURCE_REFERENCE_SUFFIXES = {".cs", ".gd", ".godot", ".tres", ".tscn"}
ASSET_SUFFIXES = {
    ".ase",
    ".aseprite",
    ".glb",
    ".gltf",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".ogg",
    ".png",
    ".svg",
    ".wav",
    ".webp",
}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | ASSET_SUFFIXES
MAX_TEXT_BYTES = 512 * 1024
MAX_SEARCH_TEXT = 16 * 1024

MARKDOWN_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
RESOURCE_REFERENCE = re.compile(r"['\"](res://[^'\"]+)['\"]")


def _source_files(root: Path) -> Iterable[Path]:
    for directory, folders, filenames in os.walk(root, followlinks=False):
        folders[:] = sorted(
            folder
            for folder in folders
            if not folder.startswith(".") and folder not in IGNORED_DIRECTORIES
        )
        for filename in sorted(filenames):
            path = Path(directory) / filename
            if path.suffix.casefold() not in SUPPORTED_SUFFIXES:
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved.is_file() and resolved.is_relative_to(root):
                yield resolved


def _manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in _source_files(root)
    }


def project_revision(project_root: Path) -> str:
    root = project_root.resolve()
    digest = hashlib.sha256()
    for relative, sha256 in _manifest(root).items():
        digest.update(relative.encode("utf-8") + b"\0" + bytes.fromhex(sha256))
    return "sha256:" + digest.hexdigest()


def _file_kind(path: str) -> str:
    suffix = Path(path).suffix.casefold()
    return {
        ".md": "document",
        ".tscn": "scene",
        ".gd": "script",
        ".cs": "script",
        ".py": "script",
        ".js": "script",
        ".ts": "script",
        ".tres": "resource",
        ".json": "data",
        ".yaml": "data",
        ".yml": "data",
        ".godot": "config",
        ".cfg": "config",
        ".ini": "config",
        ".toml": "config",
    }.get(suffix, "asset" if suffix in ASSET_SUFFIXES else "resource")


def _read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def _slug(value: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value.casefold(), flags=re.UNICODE)
    return slug.strip("-") or "section"


def _relative_target(root: Path, source: Path, raw_target: str) -> str | None:
    if raw_target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    target_text = raw_target.split("#", 1)[0].split("?", 1)[0]
    if not target_text:
        return None
    try:
        target = (source.parent / target_text).resolve()
    except OSError:
        return None
    if not target.is_relative_to(root):
        return ""
    if target.is_dir():
        target = target / "README.md"
    return target.relative_to(root).as_posix()


def build_graph(project_root: Path) -> dict[str, Any]:
    """Build a deterministic in-memory graph without writing project files."""
    root = project_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)

    manifest = _manifest(root)
    digest = hashlib.sha256()
    for relative, sha256 in manifest.items():
        digest.update(relative.encode("utf-8") + b"\0" + bytes.fromhex(sha256))
    revision = "sha256:" + digest.hexdigest()

    nodes: dict[str, dict[str, Any]] = {
        "project": {
            "id": "project",
            "kind": "project",
            "label": root.name,
            "source": ".",
            "details": {"revision": revision},
        }
    }
    edges: dict[tuple[str, str, str], dict[str, str]] = {}
    warnings: list[str] = []

    def add_edge(source: str, target: str, kind: str, evidence: str) -> None:
        if source in nodes and target in nodes and source != target:
            edges[(source, target, kind)] = {
                "source": source,
                "target": target,
                "kind": kind,
                "evidence": evidence,
            }

    texts: dict[str, str] = {}
    for relative, sha256 in manifest.items():
        node_id = "file:" + relative
        path = root / relative
        text = _read_text(path) if path.suffix.casefold() in TEXT_SUFFIXES else None
        details: dict[str, Any] = {"sha256": sha256}
        if text is not None:
            details["search_text"] = text[:MAX_SEARCH_TEXT]
            texts[relative] = text
        nodes[node_id] = {
            "id": node_id,
            "kind": _file_kind(relative),
            "label": path.name,
            "source": relative,
            "details": details,
        }

    for relative in manifest:
        add_edge("project", "file:" + relative, "contains", relative)

    for relative, text in texts.items():
        source_id = "file:" + relative
        if Path(relative).suffix.casefold() == ".md":
            seen_slugs: Counter[str] = Counter()
            for match in MARKDOWN_HEADING.finditer(text):
                label = match.group(2).strip()
                base_slug = _slug(label)
                seen_slugs[base_slug] += 1
                count = seen_slugs[base_slug]
                slug = base_slug if count == 1 else f"{base_slug}-{count}"
                heading_id = f"heading:{relative}#{slug}"
                line = text.count("\n", 0, match.start()) + 1
                nodes[heading_id] = {
                    "id": heading_id,
                    "kind": "heading",
                    "label": label,
                    "source": relative,
                    "details": {"level": len(match.group(1)), "line": line},
                }
                add_edge(source_id, heading_id, "declares", f"{relative}:{line}")

            for match in MARKDOWN_LINK.finditer(text):
                target = _relative_target(root, root / relative, match.group(1))
                if target is None:
                    continue
                line = text.count("\n", 0, match.start()) + 1
                if target and "file:" + target in nodes:
                    add_edge(source_id, "file:" + target, "links_to", f"{relative}:{line}")
                else:
                    warnings.append(
                        f"Unresolved Markdown link at {relative}:{line}: {match.group(1)}"
                    )

        if Path(relative).suffix.casefold() in RESOURCE_REFERENCE_SUFFIXES:
            for match in RESOURCE_REFERENCE.finditer(text):
                target = match.group(1).removeprefix("res://").split("#", 1)[0]
                line = text.count("\n", 0, match.start()) + 1
                if "file:" + target in nodes:
                    add_edge(source_id, "file:" + target, "references", f"{relative}:{line}")
                else:
                    warnings.append(
                        f"Unresolved resource reference at {relative}:{line}: {match.group(1)}"
                    )

    semantic = parse_semantic_documents(root)
    for node in semantic["nodes"]:
        nodes[node["id"]] = node
    for edge in semantic["edges"]:
        add_edge(edge["source"], edge["target"], edge["kind"], edge["evidence"])
    warnings.extend(semantic["warnings"])

    return {
        "schema_version": "0.5",
        "project_name": root.name,
        "project_type": "godot" if (root / "project.godot").is_file() else "generic",
        "revision": revision,
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(
            edges.values(), key=lambda item: (item["source"], item["target"], item["kind"])
        ),
        "warnings": sorted(set(warnings)),
    }


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> bool:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    try:
        if path.read_text("utf-8") == rendered:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(rendered, "utf-8")
    temporary.replace(path)
    return True


def _read_graph(root: Path) -> dict[str, Any] | None:
    try:
        value = json.loads((root / GRAPH_PATH).read_text("utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def rebuild_graph(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    graph = build_graph(root)
    changed = _write_json_atomic(root / GRAPH_PATH, graph)
    return {
        "status": "current",
        "revision": graph["revision"],
        "graph": str(root / GRAPH_PATH),
        "changed": changed,
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "warnings": len(graph["warnings"]),
    }


def graph_status(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    graph = _read_graph(root)
    live_revision = project_revision(root)
    if graph is None:
        status = "missing"
        indexed_revision = None
    else:
        indexed_revision = graph.get("revision")
        status = "current" if indexed_revision == live_revision else "stale"
    return {
        "status": status,
        "revision": live_revision,
        "indexed_revision": indexed_revision,
        "graph": str(root / GRAPH_PATH),
    }


def _require_graph(project_root: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    root = project_root.resolve()
    graph = _read_graph(root)
    if graph is None:
        raise FileNotFoundError(f"GameGraph index is missing: {root / GRAPH_PATH}")
    return root, graph, graph_status(root)


def graph_overview(project_root: Path) -> dict[str, Any]:
    _, graph, status = _require_graph(project_root)
    counts = Counter(node["kind"] for node in graph["nodes"])
    return {
        "status": status["status"],
        "project_name": graph["project_name"],
        "project_type": graph["project_type"],
        "revision": graph["revision"],
        "node_kinds": dict(sorted(counts.items())),
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "warnings": graph["warnings"],
    }


def search_graph(project_root: Path, query: str, *, limit: int = 20) -> dict[str, Any]:
    _, graph, status = _require_graph(project_root)
    terms = [term.casefold() for term in query.split() if term.strip()]
    limit = max(1, min(limit, 100))
    matches: list[tuple[int, dict[str, Any]]] = []
    for node in graph["nodes"]:
        identity = f"{node['label']} {node['source']}".casefold()
        details = json.dumps(node.get("details", {}), ensure_ascii=False).casefold()
        if terms and all(term in identity or term in details for term in terms):
            score = sum(2 if term in identity else 1 for term in terms)
            result = {key: node[key] for key in ("id", "kind", "label", "source")}
            matches.append((score, result))
    matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    return {
        "status": status["status"],
        "query": query,
        "results": [item[1] for item in matches[:limit]],
        "total": len(matches),
    }
